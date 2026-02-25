"""
ProtoReason: Protocol Procedural Reasoning Evaluation

Tests whether LLMs can correctly execute, troubleshoot, and reason about
experimental protocols.
"""

import json
import random
from typing import Optional
from dataclasses import dataclass
from scipy.stats import kendalltau

from bioeval.models.base import BaseEvaluator, EvalTask, EvalResult


# Sample protocols for demonstration (in production, load from protocols.io API)
SAMPLE_PROTOCOLS = {
    "western_blot": {
        "name": "Western Blot",
        "steps": [
            "Prepare cell lysate using RIPA buffer with protease inhibitors",
            "Determine protein concentration using BCA assay",
            "Prepare samples with loading buffer and heat at 95°C for 5 minutes",
            "Load equal amounts of protein (20-50 μg) into SDS-PAGE gel wells",
            "Run gel at 100V until dye front reaches bottom",
            "Transfer proteins to PVDF membrane at 100V for 1 hour",
            "Block membrane with 5% non-fat milk in TBST for 1 hour",
            "Incubate with primary antibody overnight at 4°C",
            "Wash membrane 3x with TBST for 10 minutes each",
            "Incubate with HRP-conjugated secondary antibody for 1 hour",
            "Wash membrane 3x with TBST for 10 minutes each",
            "Develop using ECL substrate and image"
        ],
        "safety": ["RIPA buffer contains detergents", "Handle heated samples carefully"],
        "calculations": ["protein_quantification", "dilution"]
    },
    "qpcr": {
        "name": "Quantitative PCR (qPCR)",
        "steps": [
            "Extract RNA using TRIzol or column-based kit",
            "Measure RNA concentration and quality (260/280 ratio)",
            "Synthesize cDNA using reverse transcriptase",
            "Design or obtain validated primers for target genes",
            "Prepare qPCR master mix with SYBR Green or TaqMan probes",
            "Add cDNA template to reaction wells",
            "Include no-template controls (NTC) and reference gene controls",
            "Run qPCR program: 95°C 10min, then 40 cycles of 95°C 15s, 60°C 1min",
            "Perform melt curve analysis for SYBR Green",
            "Analyze Ct values and calculate relative expression using ΔΔCt method"
        ],
        "safety": ["TRIzol contains phenol - use in fume hood"],
        "calculations": ["rna_dilution", "delta_delta_ct"]
    },
    "cell_culture_passage": {
        "name": "Cell Culture Passaging",
        "steps": [
            "Pre-warm media, PBS, and trypsin to 37°C",
            "Observe cells under microscope to assess confluence",
            "Aspirate spent media from flask",
            "Wash cells gently with PBS",
            "Add trypsin and incubate at 37°C until cells detach",
            "Neutralize trypsin with complete media",
            "Collect cells and centrifuge at 300g for 5 minutes",
            "Aspirate supernatant and resuspend pellet in fresh media",
            "Count cells using hemocytometer or automated counter",
            "Seed cells at appropriate density in new flask",
            "Record passage number and date"
        ],
        "safety": ["Work in biosafety cabinet", "Proper disposal of biological waste"],
        "calculations": ["cell_seeding", "split_ratio"]
    }
}


CALCULATION_TASKS = [
    {
        "id": "calc_001",
        "question": "You need to prepare 500 mL of 1X PBS from a 10X PBS stock. How much 10X PBS and water do you need?",
        "answer": {"stock_volume": "50 mL", "water_volume": "450 mL"},
        "reasoning": "For 1X from 10X: V1 × C1 = V2 × C2, so V1 = (500 mL × 1) / 10 = 50 mL stock + 450 mL water"
    },
    {
        "id": "calc_002",
        "question": "Your protein concentration is 2.5 mg/mL. You need to load 30 μg per well. What volume should you load?",
        "answer": {"volume": "12 μL"},
        "reasoning": "Volume = mass / concentration = 30 μg / 2.5 mg/mL = 30 μg / 2.5 μg/μL = 12 μL"
    },
    {
        "id": "calc_003",
        "question": "You counted 150 cells in a hemocytometer (1mm × 1mm × 0.1mm chamber). What is the cell concentration per mL?",
        "answer": {"concentration": "1.5 × 10^6 cells/mL"},
        "reasoning": "Chamber volume = 0.1 μL = 10^-4 mL. Concentration = 150 / 10^-4 = 1.5 × 10^6 cells/mL"
    },
    {
        "id": "calc_004",
        "question": "You have a primer stock at 100 μM. Prepare 100 μL of 10 μM working solution.",
        "answer": {"stock_volume": "10 μL", "water_volume": "90 μL"},
        "reasoning": "V1 × 100 μM = 100 μL × 10 μM. V1 = 10 μL stock + 90 μL water"
    },
    {
        "id": "calc_005",
        "question": "Your RNA 260/280 ratio is 1.85 and concentration is 500 ng/μL. You need 1 μg RNA for cDNA synthesis in a 20 μL reaction. How much RNA and water?",
        "answer": {"rna_volume": "2 μL", "water_volume": "18 μL", "quality": "acceptable"},
        "reasoning": "Volume = 1000 ng / 500 ng/μL = 2 μL. 260/280 of 1.85 is acceptable (1.8-2.0 range for RNA)"
    }
]


TROUBLESHOOTING_TASKS = [
    {
        "id": "trouble_001",
        "scenario": "Western Blot: No bands visible on the membrane after development",
        "experimental_details": "Target: β-actin (42 kDa), Primary antibody: 1:5000, Secondary: 1:10000, Transfer: 1 hour at 100V",
        "possible_causes": [
            "Transfer failure - proteins didn't transfer to membrane",
            "Antibody issues - wrong species, inactive, or too dilute",
            "Blocking too stringent or interfering with antibody",
            "ECL substrate expired or insufficient",
            "Target protein not expressed in sample",
            "Gel/membrane orientation incorrect during transfer"
        ],
        "diagnostic_steps": [
            "Check transfer with Ponceau S staining",
            "Verify antibody reactivity with positive control",
            "Try higher antibody concentration",
            "Check ECL with fresh substrate"
        ]
    },
    {
        "id": "trouble_002",
        "scenario": "qPCR: High Ct values (>35) for all samples including positive control",
        "experimental_details": "SYBR Green chemistry, cDNA from 1 μg RNA input, primers for GAPDH",
        "possible_causes": [
            "cDNA synthesis failed - check RT enzyme and conditions",
            "RNA degraded - verify RNA integrity",
            "Primers not working - verify primer design and concentration",
            "qPCR master mix issue - enzyme inactive",
            "Wrong annealing temperature",
            "Inhibitors in sample"
        ],
        "diagnostic_steps": [
            "Check RNA quality on gel or Bioanalyzer",
            "Verify cDNA with PCR and gel",
            "Test primers with positive control template",
            "Run gradient PCR for optimal temperature"
        ]
    },
    {
        "id": "trouble_003", 
        "scenario": "Cell Culture: Cells not attaching after passaging",
        "experimental_details": "HeLa cells, passage 15, split 1:10, plastic tissue culture flask",
        "possible_causes": [
            "Over-trypsinization damaged attachment proteins",
            "Trypsin not fully neutralized",
            "Wrong flask type (not tissue culture treated)",
            "Contamination affecting cell health",
            "Cells are senescent (high passage)",
            "Media missing essential factors (serum, growth factors)"
        ],
        "diagnostic_steps": [
            "Reduce trypsin time in next passage",
            "Check media color and clarity for contamination",
            "Verify flask is TC-treated",
            "Test with fresh low-passage cells"
        ]
    }
]


class ProtoReasonEvaluator(BaseEvaluator):
    """Evaluator for Protocol Procedural Reasoning tasks."""

    def __init__(
        self,
        model_name: str = "claude-sonnet-4-20250514",
        adapter_path: Optional[str] = None,
        use_4bit: bool = True,
    ):
        super().__init__(model_name, adapter_path=adapter_path, use_4bit=use_4bit)
        self.protocols = SAMPLE_PROTOCOLS
    
    def load_tasks(self) -> list[EvalTask]:
        """Load all ProtoReason evaluation tasks."""
        tasks = []
        
        # Step ordering tasks
        for protocol_id, protocol in self.protocols.items():
            tasks.append(self._create_ordering_task(protocol_id, protocol))
        
        # Missing step tasks
        for protocol_id, protocol in self.protocols.items():
            tasks.append(self._create_missing_step_task(protocol_id, protocol))
        
        # Calculation tasks
        for calc in CALCULATION_TASKS:
            tasks.append(self._create_calculation_task(calc))
        
        # Troubleshooting tasks
        for trouble in TROUBLESHOOTING_TASKS:
            tasks.append(self._create_troubleshooting_task(trouble))
        
        return tasks
    
    def _create_ordering_task(self, protocol_id: str, protocol: dict) -> EvalTask:
        """Create a step ordering task."""
        steps = protocol["steps"].copy()
        correct_order = list(range(len(steps)))
        random.shuffle(steps)
        
        prompt = f"""The following steps for {protocol['name']} are in random order. 
Please reorder them into the correct sequence by providing the step numbers in order.

Shuffled steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(steps))}

Provide your answer as a comma-separated list of step numbers in the correct order.
Then briefly explain the reasoning for critical ordering decisions."""

        return EvalTask(
            id=f"ordering_{protocol_id}",
            component="protoreason",
            task_type="step_ordering",
            prompt=prompt,
            ground_truth={
                "correct_steps": protocol["steps"],
                "shuffled_steps": steps
            }
        )
    
    def _create_missing_step_task(self, protocol_id: str, protocol: dict) -> EvalTask:
        """Create a missing step detection task."""
        steps = protocol["steps"].copy()
        
        # Remove 1-2 random steps
        num_to_remove = random.randint(1, 2)
        removed_indices = random.sample(range(len(steps)), num_to_remove)
        removed_steps = [steps[i] for i in sorted(removed_indices, reverse=True)]
        for i in sorted(removed_indices, reverse=True):
            steps.pop(i)
        
        prompt = f"""The following protocol for {protocol['name']} is missing one or more critical steps.
Identify what is missing and explain why each missing step is important.

Protocol steps:
{chr(10).join(f'{i+1}. {step}' for i, step in enumerate(steps))}

What steps are missing? Why are they critical?"""

        return EvalTask(
            id=f"missing_{protocol_id}",
            component="protoreason",
            task_type="missing_step",
            prompt=prompt,
            ground_truth={
                "removed_steps": removed_steps,
                "removed_indices": removed_indices,
                "complete_protocol": protocol["steps"]
            }
        )
    
    def _create_calculation_task(self, calc: dict) -> EvalTask:
        """Create a calculation task."""
        prompt = f"""Solve this laboratory calculation problem. Show your work step by step.

{calc['question']}

Provide:
1. The calculation steps
2. The final answer with units
3. Any important considerations or assumptions"""

        return EvalTask(
            id=calc["id"],
            component="protoreason",
            task_type="calculation",
            prompt=prompt,
            ground_truth=calc
        )
    
    def _create_troubleshooting_task(self, trouble: dict) -> EvalTask:
        """Create a troubleshooting task."""
        prompt = f"""You are troubleshooting an experimental problem. Provide a systematic diagnosis.

Scenario: {trouble['scenario']}

Experimental details: {trouble['experimental_details']}

Please provide:
1. A ranked list of possible causes (most likely first)
2. Diagnostic steps to identify the root cause
3. Recommended solutions for the top causes"""

        return EvalTask(
            id=trouble["id"],
            component="protoreason",
            task_type="troubleshooting",
            prompt=prompt,
            ground_truth=trouble
        )
    
    def score_response(self, task: EvalTask, response: str) -> dict:
        """Score a model response based on task type."""
        if task.task_type == "step_ordering":
            return self._score_ordering(task, response)
        elif task.task_type == "missing_step":
            return self._score_missing_step(task, response)
        elif task.task_type == "calculation":
            return self._score_calculation(task, response)
        elif task.task_type == "troubleshooting":
            return self._score_troubleshooting(task, response)
        else:
            return {"error": f"Unknown task type: {task.task_type}"}
    
    def _score_ordering(self, task: EvalTask, response: str) -> dict:
        """Score step ordering task using Kendall's tau."""
        # In production: parse response to extract ordering
        # For now, return placeholder
        return {
            "kendall_tau": None,  # Compute after parsing
            "critical_pairs_correct": None,
            "requires_manual_parsing": True,
            "response_length": len(response)
        }
    
    def _score_missing_step(self, task: EvalTask, response: str) -> dict:
        """Score missing step detection."""
        removed_steps = task.ground_truth["removed_steps"]
        response_lower = response.lower()
        
        # Check if key concepts from removed steps are mentioned
        detected = 0
        for step in removed_steps:
            # Extract key terms from step
            key_terms = [term for term in step.lower().split() 
                        if len(term) > 4 and term not in ['with', 'using', 'from', 'into', 'until']]
            if any(term in response_lower for term in key_terms[:3]):
                detected += 1
        
        return {
            "recall": detected / len(removed_steps) if removed_steps else 0,
            "num_removed": len(removed_steps),
            "num_detected": detected,
            "response_length": len(response)
        }
    
    def _score_calculation(self, task: EvalTask, response: str) -> dict:
        """Score calculation task."""
        correct_answer = task.ground_truth.get("answer", {})
        response_lower = response.lower()
        
        # Check if key numerical values appear in response
        values_found = 0
        total_values = len(correct_answer)
        
        for key, value in correct_answer.items():
            # Extract number from value string
            if any(char.isdigit() for char in str(value)):
                # Simple check: does the number appear?
                numbers = ''.join(c for c in str(value) if c.isdigit() or c == '.')
                if numbers in response:
                    values_found += 1
        
        return {
            "numerical_accuracy": values_found / total_values if total_values > 0 else 0,
            "shows_work": "=" in response or "therefore" in response_lower,
            "response_length": len(response)
        }
    
    def _score_troubleshooting(self, task: EvalTask, response: str) -> dict:
        """Score troubleshooting task."""
        possible_causes = task.ground_truth.get("possible_causes", [])
        response_lower = response.lower()
        
        # Check coverage of known causes
        causes_mentioned = 0
        for cause in possible_causes:
            key_terms = [term for term in cause.lower().split() 
                        if len(term) > 4][:3]
            if any(term in response_lower for term in key_terms):
                causes_mentioned += 1
        
        return {
            "cause_coverage": causes_mentioned / len(possible_causes) if possible_causes else 0,
            "causes_mentioned": causes_mentioned,
            "total_known_causes": len(possible_causes),
            "provides_diagnostics": "check" in response_lower or "verify" in response_lower,
            "response_length": len(response)
        }


def run_protoreason_evaluation(model_name: str = "claude-sonnet-4-20250514") -> dict:
    """Run full ProtoReason evaluation."""
    evaluator = ProtoReasonEvaluator(model_name)
    tasks = evaluator.load_tasks()
    results = evaluator.run_evaluation(tasks)
    
    # Aggregate by task type
    by_type = {}
    for result in results:
        task_type = result.task_id.split("_")[0]
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
    evaluator = ProtoReasonEvaluator()
    tasks = evaluator.load_tasks()
    print(f"Loaded {len(tasks)} tasks")
    for task in tasks[:3]:
        print(f"- {task.id}: {task.task_type}")
