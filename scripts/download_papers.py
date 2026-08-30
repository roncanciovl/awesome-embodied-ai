"""
Script de descarga de papers para Awesome Embodied AI.
Descarga PDFs desde arXiv (mirror export.arxiv.org) con reintentos y validación.

Uso:
    python download_papers.py
"""

import os
import sys
import time
import urllib.request
import urllib.error

# Ruta base: awesome-embodied-ai/papers/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "papers"))

# User-Agent para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (research-paper-collection; contact: roncanciovl@github)"
}

# Lista de papers: (carpeta_destino, nombre_archivo, arxiv_id)
PAPERS = [
    # ── 01_VLA_Models ──────────────────────────────────────────────
    ("01_VLA_Models", "OpenVLA_An_Open-Source_Vision-Language-Action_Model.pdf", "2406.09246"),
    ("01_VLA_Models", "RT-1_Robotics_Transformer_for_Real-World_Control_at_Scale.pdf", "2212.06817"),
    ("01_VLA_Models", "RT-2_Vision-Language-Action_Models_Transfer_Web_Knowledge.pdf", "2307.15818"),
    ("01_VLA_Models", "Octo_An_Open-Source_Generalist_Robot_Policy.pdf", "2405.12213"),
    ("01_VLA_Models", "Open_X-Embodiment_Robotic_Learning_Datasets_and_RTX_Models.pdf", "2310.08864"),
    ("01_VLA_Models", "pi0_Vision-Language-Action_Flow_Models.pdf", "2410.24164"),

    # ── 02_Simulation_Environments ─────────────────────────────────
    ("02_Simulation_Environments", "Habitat_A_Platform_for_Embodied_AI_Research.pdf", "1904.01201"),
    ("02_Simulation_Environments", "AI2-THOR_An_Interactive_3D_Environment_for_Visual_AI.pdf", "1712.05474"),
    ("02_Simulation_Environments", "iGibson_A_Simulation_Environment_for_Interactive_Tasks.pdf", "2008.11765"),
    ("02_Simulation_Environments", "Habitat-Matterport_3D_Dataset.pdf", "2109.08238"),
    ("02_Simulation_Environments", "RoboCasa_Large-Scale_Simulation_of_Everyday_Tasks.pdf", "2406.02523"),

    # ── 03_Sim2Real_RL ─────────────────────────────────────────────
    ("03_Sim2Real_RL", "Domain_Randomization_for_Transferring_DNNs_from_Simulation.pdf", "1703.06907"),
    ("03_Sim2Real_RL", "Sim-to-Real_Transfer_of_Robotic_Control_with_Dynamics_Randomization.pdf", "1710.06537"),
    ("03_Sim2Real_RL", "Learning_Quadrupedal_Locomotion_over_Challenging_Terrain.pdf", "1910.11100"),
    ("03_Sim2Real_RL", "Sim-to-Real_Transfer_for_Dexterous_Manipulation.pdf", "1910.07113"),
    ("03_Sim2Real_RL", "Asymmetric_Actor-Critic_for_Sim-to-Real.pdf", "1910.07113v1"),  # placeholder, se valida abajo
    ("03_Sim2Real_RL", "Teacher-Student_Framework_for_Sim-to-Real_Locomotion.pdf", "2009.03317"),
    ("03_Sim2Real_RL", "RMA_Rapid_Motor_Adaptation_for_Legged_Robots.pdf", "2107.04034"),

    # ── 04_Robotics_Frameworks ─────────────────────────────────────
    ("04_Robotics_Frameworks", "ROS2_Architecture_and_Performance.pdf", "2202.01734"),
    ("04_Robotics_Frameworks", "MoveIt2_and_Real-Time_Manipulation.pdf", "2405.13268"),

    # ── 05_Surveys_Case_Studies ────────────────────────────────────
    ("05_Surveys_Case_Studies", "A_Survey_of_Embodied_AI_From_Sim-to-Real.pdf", "2407.01738"),
    ("05_Surveys_Case_Studies", "Vision-Language-Action_Models_Survey.pdf", "2411.13548"),
    ("05_Surveys_Case_Studies", "Embodied_AI_Survey_Recent_Advances.pdf", "2311.11267"),
    ("05_Surveys_Case_Studies", "SayPlan_Grounding_LLMs_using_3D_Graphs.pdf", "2309.11489"),

    # ── 06_ROS2_AI_LLMs ────────────────────────────────────────────
    ("06_ROS2_AI_LLMs", "SayCan_Grounding_Language_in_Robotic_Affordances.pdf", "2204.01691"),
    ("06_ROS2_AI_LLMs", "Code_as_Policies_Language_Model_Programs_for_Robots.pdf", "2209.07753"),
    ("06_ROS2_AI_LLMs", "Inner_Monologue_Embodied_Reasoning_with_Language_Models.pdf", "2207.05608"),
    ("06_ROS2_AI_LLMs", "VoxPoser_Composable_3D_Value_Maps_with_Language_Models.pdf", "2307.05973"),
    ("06_ROS2_AI_LLMs", "ChatGPT_for_Robotics_Design_Principles_and_Model_Abilities.pdf", "2306.17582"),
    ("06_ROS2_AI_LLMs", "TidyBot_Personalized_Robot_Assistance_with_LLMs.pdf", "2305.05706"),
    ("06_ROS2_AI_LLMs", "LLM+P_Empowering_LLMs_with_Optimal_Planning.pdf", "2304.11477"),

    # ── 07_Recent_2025_2026 (selección ROS 2 + LLMs robóticos) ─────
    ("07_Recent_2025_2026", "ROS2SmolVLA_Small_VLA_for_ROS2_Industrial_2026.pdf", "2608.23320"),
    ("07_Recent_2025_2026", "ROS2_Wrapper_Florence-2_Local_VLM_2026.pdf", "2604.01179"),
    ("07_Recent_2025_2026", "Conversational_Framework_HRI_Manipulation_GenAI_2026.pdf", "2606.06061"),
    ("07_Recent_2025_2026", "Quantized_LLMs_Edge_AI_Robotics_2025.pdf", "2506.09581"),
    ("07_Recent_2025_2026", "Harness_Engineering_Physical_AI_Middleware_2026.pdf", "2606.09416"),
    ("07_Recent_2025_2026", "TurboVLA_Real-Time_VLA_32Hz_2026.pdf", "2607.27205"),
    ("07_Recent_2025_2026", "CoRAL_Contact-Rich_LLM_Control_Manipulation_2026.pdf", "2605.02600"),
    ("07_Recent_2025_2026", "Semantic_Autonomy_VLM_Indoor_Mobile_Robots_2026.pdf", "2605.02525"),
    ("07_Recent_2025_2026", "Embodied_Agentic_AI_Survey_LLM_VLM_Robot_2025.pdf", "2508.05294"),
    ("07_Recent_2025_2026", "LiteVLA-Edge_Quantized_On-Device_Control_2026.pdf", "2603.03380"),
]

# Corregir duplicado: Asymmetric Actor-Critic real es arXiv 1910.07113 (ya usado).
# Lo reemplazamos por "Learning Agile and Dynamic Motor Skills for Legged Robots" (1901.08652)
PAPERS = [p for p in PAPERS if p[2] != "1910.07113v1"]
PAPERS.insert(
    PAPERS.index(("03_Sim2Real_RL", "Sim-to-Real_Transfer_for_Dexterous_Manipulation.pdf", "1910.07113")) + 1,
    ("03_Sim2Real_RL", "Learning_Agile_and_Dynamic_Motor_Skills_for_Legged_Robots.pdf", "1901.08652"),
)


def download_paper(folder: str, filename: str, arxiv_id: str, max_retries: int = 3) -> bool:
    """Descarga un paper desde arXiv con reintentos."""
    dest_dir = os.path.join(BASE_DIR, folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)

    # Si ya existe y es un PDF válido (>10KB y empieza con %PDF), saltar
    if os.path.exists(dest_path):
        size = os.path.getsize(dest_path)
        if size > 10_000:
            with open(dest_path, "rb") as f:
                header = f.read(4)
            if header == b"%PDF":
                print(f"  [SKIP] {filename} (ya existe, {size/1e6:.1f} MB)")
                return True
        # Archivo inválido, eliminar y re-descargar
        os.remove(dest_path)

    # Usar export.arxiv.org (mirror con menos throttling)
    url = f"https://export.arxiv.org/pdf/{arxiv_id}.pdf"

    for attempt in range(1, max_retries + 1):
        try:
            print(f"  [DL] {filename} (intento {attempt}/{max_retries})...")
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=120) as response:
                data = response.read()

            # Validar que sea PDF
            if not data.startswith(b"%PDF"):
                print(f"  [WARN] Respuesta no es PDF para {arxiv_id}, reintentando...")
                time.sleep(5 * attempt)
                continue

            with open(dest_path, "wb") as f:
                f.write(data)

            print(f"  [OK] {filename} ({len(data)/1e6:.1f} MB)")
            return True

        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            print(f"  [ERR] {e}")
            if attempt < max_retries:
                wait = 10 * attempt
                print(f"  Esperando {wait}s antes de reintentar...")
                time.sleep(wait)

    print(f"  [FAIL] No se pudo descargar {filename} (arXiv:{arxiv_id})")
    return False


def main():
    print("=" * 60)
    print("Awesome Embodied AI - Descarga de Papers")
    print(f"Destino: {BASE_DIR}")
    print("=" * 60)

    results = {"ok": [], "fail": []}

    for folder, filename, arxiv_id in PAPERS:
        print(f"\n[{folder}]")
        success = download_paper(folder, filename, arxiv_id)
        if success:
            results["ok"].append(filename)
        else:
            results["fail"].append((filename, arxiv_id))
        # Pausa entre descargas para respetar rate limits de arXiv
        time.sleep(3)

    print("\n" + "=" * 60)
    print(f"RESUMEN: {len(results['ok'])} descargados, {len(results['fail'])} fallidos")
    if results["fail"]:
        print("\nFallidos:")
        for fname, aid in results["fail"]:
            print(f"  - {fname} (arXiv:{aid})")
    print("=" * 60)

    return 0 if not results["fail"] else 1


if __name__ == "__main__":
    sys.exit(main())