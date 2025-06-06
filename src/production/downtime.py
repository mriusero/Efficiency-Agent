from datetime import timedelta

machine_errors = {
    "E001": {
        "description": "Calibration Error",
        "cause": "The machine is not correctly calibrated.",
        "solution": "Recalibrate the machine according to the manufacturer's specifications.",
        "downtime": timedelta(hours=2)
    },
    "E002": {
        "description": "Motor Overheating",
        "cause": "The motor has exceeded the maximum operating temperature.",
        "solution": "Stop the machine and let it cool down. Check the cooling system.",
        "downtime": timedelta(hours=3)
    },
    "E003": {
        "description": "Material Jam",
        "cause": "Accumulation of material in the processing area.",
        "solution": "Clean the processing area and check the feeding mechanisms.",
        "downtime": timedelta(minutes=15)
    },
    "E004": {
        "description": "Sensor Error",
        "cause": "A sensor is not functioning correctly.",
        "solution": "Check the sensor connections and replace if necessary.",
        "downtime": timedelta(hours=1, minutes=30)
    },
    "E005": {
        "description": "Power Failure",
        "cause": "Electrical supply interrupted.",
        "solution": "Check the electrical supply and fuses. Restart the machine.",
        "downtime": timedelta(minutes=30)
    },
    "E006": {
        "description": "Software Error",
        "cause": "Bug in the machine control software.",
        "solution": "Restart the software or update the firmware.",
        "downtime": timedelta(hours=1)
    },
    "E007": {
        "description": "Wear and Tear of Parts",
        "cause": "The machine parts are worn out.",
        "solution": "Inspect the parts and replace if necessary.",
        "downtime": timedelta(hours=1)
    },
    "E008": {
        "description": "Communication Error",
        "cause": "Communication problem between different machine modules.",
        "solution": "Check communication cables and protocols.",
        "downtime": timedelta(hours=2)
    },
    "E009": {
        "description": "Low Lubricant Level",
        "cause": "The lubricant level is insufficient.",
        "solution": "Refill the lubricant reservoir according to specifications.",
        "downtime": timedelta(minutes=15)
    },
    "E010": {
        "description": "Positioning Error",
        "cause": "The tooling is not positioning correctly.",
        "solution": "Check the positioning mechanisms and recalibrate if necessary.",
        "downtime": timedelta(hours=1)
    }
}