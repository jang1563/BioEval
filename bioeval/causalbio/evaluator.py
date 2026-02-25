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
            "affected_pathways": [
                {"pathway": "MAPK/ERK", "direction": "decreased", "mechanism": "Direct BRAF inhibition"},
                {"pathway": "Cell cycle", "direction": "arrested", "mechanism": "Loss of ERK-driven proliferation signals"}
            ],
            "compensatory": [
                "NRAS mutations - bypass BRAF",
                "BRAF amplification - overwhelm inhibitor",
                "MEK mutations - constitutive activation downstream",
                "RTK upregulation (EGFR, PDGFR) - alternative pathway activation"
            ],
            "expected_phenotype": "Rapid tumor regression in BRAF V600E melanoma"
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
    
    def load_tasks(self, data_tier: str = "base") -> list[EvalTask]:
        """Load CausalBio evaluation tasks.

        Args:
            data_tier: "base" (evaluator.py only), "extended" or "all"
                       (extended_data.py superset including base).
        """
        if data_tier in ("extended", "all"):
            from bioeval.causalbio.extended_data import (
                KNOCKOUT_TASKS as ko_list,
                PATHWAY_TASKS as pw_list,
                DRUG_RESPONSE_TASKS as dr_list,
                EPISTASIS_TASKS as ep_list,
            )
        else:
            ko_list = KNOCKOUT_TASKS
            pw_list = PATHWAY_TASKS
            dr_list = DRUG_RESPONSE_TASKS
            ep_list = EPISTASIS_TASKS

        tasks = []
        for ko in ko_list:
            tasks.append(self._create_knockout_task(ko))
        for pathway in pw_list:
            tasks.append(self._create_pathway_task(pathway))
        for epi in ep_list:
            tasks.append(self._create_epistasis_task(epi))
        for drug in dr_list:
            tasks.append(self._create_drug_response_task(drug))
        return tasks
    
    def _create_knockout_task(self, ko: dict) -> EvalTask:
        """Create a knockout phenotype prediction task."""
        question = ko.get('question',
                          f"What is the predicted fitness effect of {ko['gene']} knockout in {ko['cell_line']}?")
        base_prompt = f"""Predict the fitness effect of a gene knockout based on biological reasoning.

Gene: {ko['gene']}
Cell line: {ko['cell_line']} ({ko['cell_type']})

Question: {question}

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
        question = pathway.get('question',
                               f"Which downstream pathways will be affected by {pathway['perturbation']} and in what direction?")
        base_prompt = f"""Predict downstream pathway effects of a perturbation.

Perturbation: {pathway['perturbation']}
Cell context: {pathway['cell_context']}

Question: {question}

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
        # single_effects can be at top-level or inside ground_truth
        single_effects = epi.get('single_effects', epi.get('ground_truth', {}).get('single_effects', {}))
        se_a = single_effects.get(f'{epi["gene_a"]}_ko', single_effects.get(f'{epi["gene_a"]}_loss', 'unknown'))
        se_b = single_effects.get(f'{epi["gene_b"]}_ko', single_effects.get(f'{epi["gene_b"]}_loss', 'unknown'))
        question = epi.get('question',
                           f"What is the combined effect of {epi['gene_a']} and {epi['gene_b']} perturbation in {epi['context']}?")
        base_prompt = f"""Predict the genetic interaction between two genes.

Gene A: {epi['gene_a']}
Gene B: {epi['gene_b']}
Context: {epi['context']}

Known single-gene effects:
- {epi['gene_a']} knockout: {se_a}
- {epi['gene_b']} knockout: {se_b}

Question: {question}

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
        question = drug.get('question',
                            f"What genes are affected by {drug['drug']} treatment in {drug['cell_type']}?")
        base_prompt = f"""Predict the transcriptional and cellular response to drug treatment.

Drug: {drug['drug']}
Cell type: {drug['cell_type']}

Question: {question}

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
        """Score knockout prediction using structured label extraction."""
        from bioeval.scoring.response_parser import extract_categorical_label, extract_confidence_structured
        from bioeval.scoring.matching import phrase_match, extract_key_terms, matched_list

        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()

        # Extract predicted effect using parser
        label_result = extract_categorical_label(
            response, ["essential", "non-essential", "context-dependent"]
        )
        if label_result.success:
            effect_correct = label_result.value == gt["effect"]
        else:
            effect_correct = phrase_match(gt["effect"], response_lower)

        # Reasoning quality
        key_concepts = extract_key_terms(gt["explanation"], min_length=5, max_terms=5)
        matched_concepts = matched_list(key_concepts, response_lower)
        reasoning_score = len(matched_concepts) / len(key_concepts) if key_concepts else 0

        confidence_result = extract_confidence_structured(response)

        return {
            "effect_correct": effect_correct,
            "predicted_effect": label_result.value if label_result.success else "unknown",
            "expected_effect": gt["effect"],
            "extraction_method": label_result.method,
            "reasoning_score": round(reasoning_score, 3),
            "matched_concepts": matched_concepts,
            "mentions_cell_line_context": phrase_match(task.ground_truth["cell_line"], response_lower),
            "confidence": confidence_result.value if confidence_result.success else None,
            "response_length": len(response),
        }

    def _score_pathway(self, task: EvalTask, response: str) -> dict:
        """Score pathway reasoning with direction accuracy."""
        from bioeval.scoring.response_parser import extract_direction
        from bioeval.scoring.matching import phrase_match, any_match

        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()

        pathways_mentioned = 0
        direction_correct = 0
        pathway_details = []

        for pathway_info in gt["affected_pathways"]:
            pathway_name = pathway_info["pathway"]
            expected_direction = pathway_info["direction"].lower()

            name_parts = [t.lower() for t in pathway_name.split("/")]
            is_mentioned = any_match(name_parts, response_lower)
            if is_mentioned:
                pathways_mentioned += 1

            dir_result = extract_direction(response, target=pathway_name)
            dir_map = {
                "decreased": "down", "reduced": "down", "inhibited": "down",
                "blocked": "down", "arrested": "down", "suppressed": "down",
                "downregulated": "down", "attenuated": "down", "diminished": "down",
                "repressed": "down", "abolished": "down", "impaired": "down",
                "increased": "up", "activated": "up", "enhanced": "up",
                "upregulated": "up", "stimulated": "up", "induced": "up",
                "elevated": "up", "amplified": "up", "promoted": "up",
            }
            expected_normalized = dir_map.get(expected_direction, expected_direction)
            dir_correct = dir_result.success and dir_result.value == expected_normalized
            if dir_correct:
                direction_correct += 1

            pathway_details.append({
                "pathway": pathway_name,
                "mentioned": is_mentioned,
                "expected_direction": expected_normalized,
                "predicted_direction": dir_result.value if dir_result.success else None,
                "direction_correct": dir_correct,
            })

        total_pathways = len(gt["affected_pathways"])
        pathway_coverage = pathways_mentioned / total_pathways if total_pathways > 0 else 0
        direction_accuracy = direction_correct / total_pathways if total_pathways > 0 else 0

        compensatory = gt.get("compensatory", [])
        comp_mentioned = sum(
            1 for c in compensatory
            if any(phrase_match(term.lower(), response_lower) for term in c.split()[:3] if len(term) > 4)
        )

        return {
            "pathway_coverage": round(pathway_coverage, 3),
            "direction_accuracy": round(direction_accuracy, 3),
            "combined_score": round((pathway_coverage + direction_accuracy) / 2, 3),
            "pathways_mentioned": pathways_mentioned,
            "direction_correct": direction_correct,
            "total_pathways": total_pathways,
            "compensatory_mentioned": comp_mentioned,
            "pathway_details": pathway_details,
            "response_length": len(response),
        }

    def _score_epistasis(self, task: EvalTask, response: str) -> dict:
        """Score epistasis reasoning with structured interaction type extraction."""
        from bioeval.scoring.response_parser import extract_interaction_type
        from bioeval.scoring.matching import extract_key_terms, matched_list, any_match

        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()

        type_result = extract_interaction_type(response)
        gt_type = gt.get("interaction", gt.get("interaction_type", "")).lower()
        type_normalization = {
            "synergistic": "synergistic", "suppressive": "suppressive",
            "enhancing": "enhancing", "synthetic_lethal": "synthetic_lethal",
        }
        expected_type = type_normalization.get(gt_type, gt_type)
        interaction_correct = type_result.success and type_result.value == expected_type

        mechanism_terms = extract_key_terms(gt["mechanism"], min_length=5, max_terms=5)
        matched_mechanism = matched_list(mechanism_terms, response_lower)
        mechanism_score = len(matched_mechanism) / len(mechanism_terms) if mechanism_terms else 0

        clinical_terms = extract_key_terms(gt.get("clinical_relevance", ""), min_length=5, max_terms=3)
        clinical_mentioned = any_match(clinical_terms, response_lower) if clinical_terms else False

        return {
            "interaction_type_correct": interaction_correct,
            "predicted_type": type_result.value if type_result.success else "unknown",
            "expected_type": expected_type,
            "extraction_method": type_result.method,
            "mechanism_score": round(mechanism_score, 3),
            "matched_mechanism_terms": matched_mechanism,
            "mentions_clinical_relevance": clinical_mentioned,
            "response_length": len(response),
        }

    def _score_drug_response(self, task: EvalTask, response: str) -> dict:
        """Score drug response prediction with directional accuracy."""
        from bioeval.scoring.response_parser import extract_gene_directions
        from bioeval.scoring.matching import phrase_match, any_match, extract_key_terms

        gt = task.ground_truth["ground_truth"]
        response_lower = response.lower()

        gene_result = extract_gene_directions(response)

        up_correct = 0
        down_correct = 0
        up_mentioned = 0
        down_mentioned = 0

        for gene in gt["upregulated"]:
            gene_name = gene.split("/")[0].upper()
            mentioned = phrase_match(gene_name, response_lower) or phrase_match(gene, response_lower)
            if mentioned:
                up_mentioned += 1
                if gene_result.success:
                    if gene_name in gene_result.value.get("upregulated", []):
                        up_correct += 1
                    elif gene_name not in gene_result.value.get("downregulated", []):
                        up_correct += 0.5

        for gene in gt["downregulated"]:
            gene_name = gene.split("/")[0].upper()
            mentioned = phrase_match(gene_name, response_lower) or phrase_match(gene, response_lower)
            if mentioned:
                down_mentioned += 1
                if gene_result.success:
                    if gene_name in gene_result.value.get("downregulated", []):
                        down_correct += 1
                    elif gene_name not in gene_result.value.get("upregulated", []):
                        down_correct += 0.5

        total_genes = len(gt["upregulated"]) + len(gt["downregulated"])
        gene_mention_rate = (up_mentioned + down_mentioned) / total_genes if total_genes > 0 else 0
        direction_accuracy = (up_correct + down_correct) / total_genes if total_genes > 0 else 0

        mech_terms = extract_key_terms(gt.get("mechanism", ""), min_length=5, max_terms=3)
        mechanism_mentioned = any_match(mech_terms, response_lower)

        phenotype = gt.get("phenotype", "")
        phenotype_terms = [t.strip().lower() for t in phenotype.split(",") if len(t.strip()) > 3]
        phenotype_mentioned = any_match(phenotype_terms, response_lower) if phenotype_terms else False

        return {
            "gene_mention_rate": round(gene_mention_rate, 3),
            "direction_accuracy": round(direction_accuracy, 3),
            "combined_score": round((gene_mention_rate + direction_accuracy) / 2, 3),
            "upregulated_mentioned": up_mentioned,
            "upregulated_direction_correct": up_correct,
            "downregulated_mentioned": down_mentioned,
            "downregulated_direction_correct": down_correct,
            "total_expected_genes": total_genes,
            "mechanism_mentioned": mechanism_mentioned,
            "phenotype_mentioned": phenotype_mentioned,
            "response_length": len(response),
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
