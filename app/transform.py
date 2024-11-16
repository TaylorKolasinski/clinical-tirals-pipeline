import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def transform_data(raw_data):
    """
    Transform raw clinical trial data into a standardized format.

    Args:
        raw_data (list or dict): Raw data fetched from the ingestion pipeline.

    Returns:
        list: Transformed list of clinical trial dictionaries.
    """
    logging.info("Starting data transformation.")
    transformed_trials = []
    try:
        # Determine input type and extract studies
        if isinstance(raw_data, dict):
            studies = raw_data.get("FullStudiesResponse", {}).get("FullStudies", [])
        elif isinstance(raw_data, list):
            studies = raw_data
        else:
            raise ValueError("Invalid raw_data format: Expected dict or list.")

        for study in studies:
            try:
                # Parse nested sections
                protocol_section = (
                    study.get("Study", {}).get("ProtocolSection", {})
                    if isinstance(study, dict) and "Study" in study
                    else study.get("protocolSection", {})
                )
                identification_module = (
                    protocol_section.get("IdentificationModule", {}) or
                    protocol_section.get("identificationModule", {})
                )
                design_module = (
                    protocol_section.get("DesignModule", {}) or
                    protocol_section.get("designModule", {})
                )
                arms_interventions_module = (
                    protocol_section.get("ArmsInterventionsModule", {}) or
                    protocol_section.get("armsInterventionsModule", {})
                )
                status_module = (
                    protocol_section.get("StatusModule", {}) or
                    protocol_section.get("statusModule", {})
                )

                # Extract required fields
                nct_number = identification_module.get("NCTId") or identification_module.get("nctId", "Unknown")
                title = identification_module.get("BriefTitle") or identification_module.get("briefTitle", "Untitled")
                if nct_number == "Unknown" or title == "Untitled":
                    logging.warning(f"Skipping study due to missing required fields: NCTId={nct_number}, Title={title}")
                    continue

                # Extract optional fields with defaults
                phase = (
                    design_module.get("PhaseList", {}).get("Phase", "N/A")
                    if "PhaseList" in design_module
                    else design_module.get("phases", ["N/A"])[0]
                )
                interventions = (
                    arms_interventions_module.get("InterventionList", {}).get("Intervention", [{}])
                    or arms_interventions_module.get("interventions", [{}])
                )
                intervention_name = (
                    interventions[0].get("InterventionName")
                    or interventions[0].get("name", "N/A")
                    if interventions
                    else "N/A"
                )
                status = status_module.get("OverallStatus") or status_module.get("overallStatus", "N/A")
                last_update_raw = (
                    status_module.get("LastUpdatePostDateStruct", {}).get("LastUpdatePostDate") or
                    status_module.get("lastUpdatePostDateStruct", {}).get("date")
                )
                last_update = None
                if last_update_raw:
                    try:
                        last_update = datetime.strptime(last_update_raw, "%Y-%m-%d").date()
                    except ValueError:
                        logging.warning(f"Invalid date format for study {nct_number}: {last_update_raw}")

                # Construct the trial dictionary
                trial = {
                    "nct_number": nct_number,
                    "title": title,
                    "phase": phase,
                    "intervention": intervention_name,
                    "status": status,
                    "last_update": last_update,
                }
                transformed_trials.append(trial)
            except Exception as inner_e:
                logging.warning(f"Error processing study: {inner_e}")
                continue

        logging.info(f"Transformed {len(transformed_trials)} trials.")
    except Exception as e:
        logging.error(f"Error transforming data: {e}", exc_info=True)
        raise
    return transformed_trials
