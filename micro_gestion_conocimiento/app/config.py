"""Este archivo contiene la configuración de la aplicación (Rutas,)."""
from pathlib import Path

pathOWL = str(Path(__file__).resolve().parent / "infraestructure" / "OWL")
ontologia = str(Path(pathOWL) / "ontologiav18.owl")
ontologiaInstanciada = str(Path(pathOWL) / "ontologiaInstanciada.owl")