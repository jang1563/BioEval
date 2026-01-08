"""
CausalBio: Causal Perturbation Prediction Evaluation

Tests whether LLMs can predict biological outcomes from genetic/chemical
perturbations using experimental data as ground truth.
"""

import json
from typing import Optional
from dataclasses import dataclass

from bioeval.models.base import BaseEvaluator, EvalTask
from bioeval.prompts import (
    enhance_causal_prompt,
    add_calibration_instructions,
    add_edge_case_check,
    PromptEnhancementConfig,
    SCIENTIFIC_REASONING_SYSTEM_PROMPT,
)
from bioeval import config


# Sample perturbation tasks (in production, load from DepMap/CMap)
# These represent real biological knowledge that can be validated against experimental data
KNOCKOUT_TASKS = [
    {
        "id": "ko_001",
        "gene": "TP53",
        "cell_line": "A549",
        "cell_type": "lung adenocarcinoma",
        "question": "What is the expected fitness effect of TP53 knockout?",
        "ground_truth": {
            "effect": "non-essential",
            "crispr_score": 0.12,  # Near zero = non-essential in this context
            "explanation": "TP53 is already mutated/inactive in A549, so knockout has minimal effect"
        },
        "reasoning_required": "Understanding that A549 has existing TP53 mutation"
    },
    {
        "id": "ko_002",
        "gene": "KRAS",
        "cell_line": "A549",
        "cell_type": "lung adenocarcinoma",
        "question": "What is the expected fitness effect of KRAS knockout?",
        "ground_truth": {
            "effect": "essential",
            "crispr_score": -1.2,  # Negative = essential (cells die)
            "explanation": "A549 is KRAS-mutant and dependent on KRAS signaling"
        },
        "reasoning_required": "Understanding oncogene addiction in KRAS-mutant cancers"
    },
    {
        "id": "ko_003",
        "gene": "BRCA1",
        "cell_line": "HCC1937",
        "cell_type": "breast cancer (BRCA1-mutant)",
        "question": "What is the expected fitness effect of BRCA1 knockout?",
        "ground_truth": {
            "effect": "non-essential",
            "crispr_score": 0.05,
            "explanation": "HCC1937 already has BRCA1 loss-of-function, additional knockout has no effect"
        },
        "reasoning_required": "Understanding pre-existing mutations"
    },
    {
        "id": "ko_004",
        "gene": "PARP1",
        "cell_line": "HCC1937",
        "cell_type": "breast cancer (BRCA1-mutant)",
        "question": "What is the expected fitness effect of PARP1 knockout?",
        "ground_truth": {
            "effect": "essential",
            "crispr_score": -0.9,
            "explanation": "Synthetic lethality - BRCA1-deficient cells depend on PARP for DNA repair"
        },
        "reasoning_required": "Understanding synthetic lethality and DNA repair pathway compensation"
    },
    {
        "id": "ko_005",
        "gene": "MYC",
        "cell_line": "K562",
        "cell_type": "chronic myeloid leukemia",
        "question": "What is the expected fitness effect of MYC knockout?",
        "ground_truth": {
            "effect": "essential",
            "crispr_score": -1.5,
            "explanation": "MYC is a master regulator of cell proliferation, essential in most cancer cells"
        },
        "reasoning_required": "Understanding core proliferation dependencies"
    }
]


PATHWAY_TASKS = [
    {
        "id": "pathway_001",
        "perturbation": "EGFR inhibitor (erlotinib)",
        "cell_context": "EGFR-mutant lung cancer",
        "question": "Which downstream pathways will be affected and in what direction?",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "MAPK/ERK", "direction": "decreased", "mechanism": "RAS-RAF-MEK-ERK blocked"},
                {"pathway": "PI3K/AKT", "direction": "decreased", "mechanism": "PI3K activation reduced"},
                {"pathway": "STAT3", "direction": "decreased", "mechanism": "Direct EGFR-STAT3 signaling blocked"}
            ],
            "expected_phenotype": "Growth arrest, apoptosis in sensitive cells"
        }
    },
    {
        "id": "pathway_002",
        "perturbation": "mTOR inhibitor (rapamycin)",
        "cell_context": "general cancer cells",
        "question": "Which downstream pathways will be affected and what compensatory mechanisms might emerge?",
        "ground_truth": {
            "affected_pathways": [
                {"pathway": "mTORC1 targets", "direction": "decreased", "mechanism": "S6K, 4EBP1 phosphorylation reduced"},
                {"pathway": "Protein synthesis", "direction": "decreased", "mechanism": "Translation initiation impaired"},
                {"pathway": "Autophagy", "direction": "increased", "mechanism": "mTORC1 inhibition releases autophagy suppression"}
            ],
            "compensatory": ["AKT activation via loss of S6K negative feedback", "mTORC2 signaling may increase"],
            "expected_phenotype": "Cytostatic effect, autophagy induction"
        }
    },
    {
        "id": "pathway_003",
        "perturbation": "BRAF V600E inhibitor (vemurafenib)",
        "cell_context": "BRAF V600E melanoma",
        "question": "Predict immediate effects and potential resistance mechanisms.",
        "ground_truth": {
            "immediate_effects": [
                {"pathway": "MAPK/ERK", "direction": "decreased", "mechanism": "Direct BRAF inhibition"},
                {"pathway": "Cell cycle", "direction": "arrested", "mechanism": "Loss of ERK-driven proliferation signals"}
            ],
            "resistance_mechanisms": [
                "NRAS mutations - bypass BRAF",
                "BRAF amplification - overwhelm inhibitor",
                "MEK mutations - constitutive activation downstream",
                "RTK upregulation (EGFR, PDGFR) - alternative pathway activation"
            ]
        }
    }
]


EPISTASIS_TASKS = [
    {
        "id": "epistasis_001",
        "gene_a": "KRAS",
        "gene_b": "STK11",
        "context": "lung cancer",
        "single_effects": {
            "KRAS_ko": "lethal in KRAS-mutant cells",
            "STK11_ko": "enhanced proliferation"
        },
        "question": "In KRAS-mutant lung cancer, what is the effect of STK11 loss?",
        "ground_truth": {
            "interaction": "enhancing",
            "combined_effect": "Increased aggressiveness, metabolic rewiring",
            "mechanism": "STK11 loss removes metabolic checkpoint, allowing KRAS-driven growth",
            "clinical_relevance": "KRAS-STK11 co-mutation associated with poor prognosis"
        }
    },
    {
        "id": "epistasis_002",
        "gene_a": "BRCA1",
        "gene_b": "53BP1",
        "context": "breast cancer",
        "single_effects": {
            "BRCA1_ko": "HR deficiency, PARP sensitivity",
            "53BP1_ko": "Partial rescue of BRCA1 loss"
        },
        "question": "What happens when 53BP1 is lost in BRCA1-deficient cells?",
        "ground_truth": {
            "interaction": "suppressive",
            "combined_effect": "Partial rescue of HR, PARP inhibitor resistance",
            "mechanism": "53BP1 loss allows resection in BRCA1-deficient cells, partially restoring HR",
            "clinical_relevance": "53BP1 loss is a mechanism of PARP inhibitor resistance"
        }
    },
    {
        "id": "epistasis_003",
        "gene_a": "RB1",
        "gene_b": "TP53",
        "context": "small cell lung cancer transformation",
        "single_effects": {
            "RB1_ko": "Loss of cell cycle checkpoint",
            "TP53_ko": "Loss of DNA damage checkpoint"
        },
        "question": "What is the combined effect of RB1 and TP53 loss?",
        "ground_truth": {
            "interaction": "synergistic",
            "combined_effect": "Enables neuroendocrine transformation, small cell phenotype",
            "mechanism": "Combined checkpoint loss allows lineage plasticity",
            "clinical_relevance": "RB1/TP53 co-loss seen in SCLC and transformed EGFR-mutant NSCLC"
        }
    }
]


DRUG_RESPONSE_TASKS = [
    {
        "id": "drug_001",
        "drug": "Dexamethasone",
        "cell_type": "T lymphocytes",
        "question": "Predict the transcriptional response to dexamethasone treatment.",
        "ground_truth": {
            "upregulated": ["GILZ/TSC22D3", "FKBP5", "DUSP1", "anti-inflammatory genes"],
            "downregulated": ["IL2", "IFNG", "TNF", "pro-inflammatory cytokines"],
            "mechanism": "GR-mediated transcriptional regulation",
            "phenotype": "Immunosuppression, T cell apoptosis"
        }
    },
    {
        "id": "drug_002",
        "drug": "Imatinib",
        "cell_type": "BCR-ABL+ CML cells",
        "question": "Predict the cellular response to imatinib treatment.",
        "ground_truth": {
            "upregulated": ["BIM/BCL2L11", "p27/CDKN1B", "pro-apoptotic genes"],
            "downregulated": ["MYC", "CCND1", "BCL2", "survival genes"],
            "mechanism": "BCR-ABL kinase inhibition",
            "phenotype": "Cell cycle arrest, apoptosis"
        }
    }
]


class CausalBioEvaluator(BaseEvaluator):
    """Evaluator for Causal Perturbation Prediction tasks."""

    def __init__(self, model_name: str = "claude-sonnet-4-20250514", use_enhanced_prompts: bool = True):
        super().__init__(model_name)
        self.use_enhanced_prompts = use_enhanced_prompts and config.PROMPT_ENHANCEMENTS_ENABLED
        self.enhancement_config = PromptEnhancementConfig(
            calibration=config.ENHANCEMENT_CALIBRATION,
            context_defense=config.ENHANCEMENT_CONTEXT_DEFENSE,
            edge_case=config.ENHANCEMENT_EDGE_CASE,
            nonsense_detection=config.ENHANCEMENT_NONSENSE_DETECTION,
            chain_of_thought=config.ENHANCEMENT_CHAIN_OF_THOUGHT,
        )
        self.system_prompt = SCIENTIFIC_REASONING_SYSTEM_PROMPT if self.use_enhanced_prompts else None
    
    def load_tasks(self) -> list[EvalTask]:
        """Load all CausalBio evaluation tasks."""
        tasks = []
        
        # Knockout prediction tasks
        for ko in KNOCKOUT_TASKS:
            tasks.append(self._create_knockout_task(ko))
        
        # Pathway reasoning tasks
        for pathway in PATHWAY_TASKS:
            tasks.append(self._create_pathway_task(pathway))
        
        # Epistasis reasoning tasks
        for epi in EPISTASIS_TASKS:
            tasks.append(self._create_epistasis_task(epi))
        
        # Drug response tasks
        for drug in DRUG_RESPONSE_TASKS:
            tasks.append(self._create_drug_response_task(drug))
        
        return tasks
    
    def _create_knockout_task(self, ko: dict) -> EvalTask:
        """Create a knockout phenotype prediction task."""
        base_prompt = f"""Predict the fitness effect of a gene knockout based on biological reasoning.

Gene: {ko['gene']}
Cell line: {ko['cell_line']} ({ko['cell_type']})

Question: {ko['question']}

Provide:
1. Your prediction: Is this gene essential, non-essential, or context-dependent in this cell line?
2. Confidence level (high/medium/low)
3. Biological reasoning for your prediction
4. What experimental evidence would you expect to see?"""

        # Apply enhanced prompts for causal reasoning
        if self.use_enhanced_prompts:
            prompt = enhance_causal_prompt(base_prompt, self.enhancement_config)
        else:
            prompt = base_prompt

        return EvalTask(
            id=ko["id"],
            component="causalbio",
            task_type="knockout_prediction",
            prompt=prompt,
            ground_truth=ko,
            system_prompt=self.system_prompt
        )
    
    def _create_pathway_task(self, pathway: dict) -> EvalTask:
        """Create a pathway reasoning task."""
        base_prompt = f"""Predict downstream pathway effects of a perturbation.

Perturbation: {pathway['perturbation']}
Cell context: {pathway['cell_context']}

Question: {pathway['question']}

Provide:
1. List of affected pathways and direction of change (increased/decreased)
2. Molecular mechanism for each pathway effect
3. Expected cellular phenotype
4. Any compensatory or feedback mechanisms that might emerge"""

        # Apply enhanced prompts for causal reasoning
        if self.use_enhanced_prompts:
            prompt = enhance_causal_prompt(base_prompt, self.enhancement_config)
        else:
            prompt = base_prompt

        return EvalTask(
            id=pathway["id"],
            component="causalbio",
            task_type="pathway_reasoning",
            prompt=prompt,
            ground_truth=pathway,
            system_prompt=self.system_prompt
        )
    
    def _create_epistasis_task(self, epi: dict) -> EvalTask:
        """Create an epistasis reasoning task."""
        base_prompt = f"""Predict the genetic interaction between two genes.

Gene A: {epi['gene_a']}
Gene B: {epi['gene_b']}
Context: {epi['context']}

Known single-gene effects:
- {epi['gene_a']} knockout: {epi['single_effects'][f'{epi["gene_a"]}_ko']}
- {epi['gene_b']} knockout: {epi['single_effects'][f'{epi["gene_b"]}_ko']}

Question: {epi['question']}

Provide:
1. Type of genetic interaction (synthetic lethal, suppressive, enhancing, no interaction)
2. Combined phenotypic effect
3. Molecular mechanism of interaction
4. Clinical or therapeutic relevance"""

        # Apply enhanced prompts for causal reasoning
        if self.use_enhanced_prompts:
            prompt = enhance_causal_prompt(base_prompt, self.enhancement_config)
        else:
            prompt = base_prompt

        return EvalTask(
            id=epi["id"],
            component="causalbio",
            task_type="epistasis",
            prompt=prompt,
            ground_truth=epi,
            system_prompt=self.system_prompt
        )
    
    def _create_drug_response_task(self, drug: dict) -> EvalTask:
        """Create a drug response prediction task."""
        base_prompt = f"""Predict the transcriptional and cellular response to drug treatment.

Drug: {drug['drug']}
Cell type: {drug['cell_type']}

Question: {drug['question']}

Provide:
1. Key genes expected to be upregulated
2. Key genes expected to be downregulated
3. Mechanism of drug action
4. Expected cellular phenotype"""

        # Apply enhanced prompts for causal reasoning
        if self.use_enhanced_prompts:
            prompt = enhance_causal_prompt(base_prompt, self.enhancement_config)
        else:
            prompt = base_prompt

        return EvalTask(
            id=drug["id"],
            component="causalbio",
            task_type="drug_response",
            prompt=prompt,
            ground_truth=drug,
            system_prompt=self.system_prompt
        )
    
    def score_response(self, task: EvalTask, response: str) -> dict:
        """Score a model response based on task type."""
        if task.task_type == "knockout_prediction":
            return self._score_knockout(task, response)
        elif task.task_type == "pathway_reasoning":
            return self._score_pathway(task, response)
        elif task.task_type == "epistasis":
            return self._score_epistasis(task, response)
        elif task.task_type == "drug_response":
            return self._score_drug_response(task, response)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}
    
    def _score_knockout(self, task: EvalTask, response: str) -> dict:
        """Score knockout prediction."""
        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()
        
        # Check if predicted effect matches
        effect_correct = gt["effect"] in response_lower
        
        # Check if reasoning mentions key concepts
        explanation_lower = gt["explanation"].lower()
        key_concepts = [word for word in explanation_lower.split() if len(word) > 4][:5]
        reasoning_score = sum(1 for concept in key_concepts if concept in response_lower) / len(key_concepts)
        
        return {
            "effect_correct": effect_correct,
            "reasoning_score": reasoning_score,
            "mentions_cell_line_context": task.ground_truth["cell_line"].lower() in response_lower,
            "response_length": len(response)
        }
    
    def _score_pathway(self, task: EvalTask, response: str) -> dict:
        """Score pathway reasoning."""
        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()
        
        # Check pathway coverage
        pathways_mentioned = 0
        for pathway_info in gt["affected_pathways"]:
            pathway_name = pathway_info["pathway"].lower()
            if any(term in response_lower for term in pathway_name.split("/")):
                pathways_mentioned += 1
        
        pathway_coverage = pathways_mentioned / len(gt["affected_pathways"])
        
        return {
            "pathway_coverage": pathway_coverage,
            "pathways_mentioned": pathways_mentioned,
            "total_pathways": len(gt["affected_pathways"]),
            "response_length": len(response)
        }
    
    def _score_epistasis(self, task: EvalTask, response: str) -> dict:
        """Score epistasis reasoning."""
        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()
        
        # Check interaction type
        interaction_correct = gt["interaction"] in response_lower
        
        # Check mechanism understanding
        mechanism_lower = gt["mechanism"].lower()
        mechanism_terms = [word for word in mechanism_lower.split() if len(word) > 4][:5]
        mechanism_score = sum(1 for term in mechanism_terms if term in response_lower) / len(mechanism_terms) if mechanism_terms else 0
        
        return {
            "interaction_type_correct": interaction_correct,
            "mechanism_score": mechanism_score,
            "mentions_clinical_relevance": "clinical" in response_lower or "resistance" in response_lower,
            "response_length": len(response)
        }
    
    def _score_drug_response(self, task: EvalTask, response: str) -> dict:
        """Score drug response prediction."""
        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()
        
        # Check gene predictions
        upregulated_found = sum(1 for gene in gt["upregulated"] 
                               if gene.lower().split("/")[0] in response_lower)
        downregulated_found = sum(1 for gene in gt["downregulated"] 
                                 if gene.lower().split("/")[0] in response_lower)
        
        total_genes = len(gt["upregulated"]) + len(gt["downregulated"])
        gene_accuracy = (upregulated_found + downregulated_found) / total_genes if total_genes > 0 else 0
        
        return {
            "gene_accuracy": gene_accuracy,
            "upregulated_found": upregulated_found,
            "downregulated_found": downregulated_found,
            "phenotype_mentioned": gt["phenotype"].split(",")[0].lower() in response_lower,
            "response_length": len(response)
        }


def run_causalbio_evaluation(model_name: str = "claude-sonnet-4-20250514") -> dict:
    """Run full CausalBio evaluation."""
    evaluator = CausalBioEvaluator(model_name)
    tasks = evaluator.load_tasks()
    results = evaluator.run_evaluation(tasks)
    
    # Aggregate by task type
    by_type = {}
    for result in results:
        task_type = [t for t in ["knockout", "pathway", "epistasis", "drug"] 
                    if t in result.task_id][0]
        if task_type not in by_type:
            by_type[task_type] = []
        by_type[task_type].append(result.scores)
    
    return {
        "model": model_name,
        "num_tasks": len(results),
        "results_by_type": by_type,
        "raw_results": [r.__dict__ for r in results]
    }


if __name__ == "__main__":
    # Quick test
    evaluator = CausalBioEvaluator()
    tasks = evaluator.load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    for task in tasks[:3]:
        print(f"- {task.id}: {task.task_type}")
