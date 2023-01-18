from component.message import cm

fcc_inputs = [
    {"text": cm.fcc.source.inputs.gfc, "value": "GFC"},
    {"text": cm.fcc.source.inputs.tmf, "value": "TMF", "disabled": True},
]

fcc_display = {"palette": ["black", "red", "orange", "green"], "min": 0, "max": 3}
