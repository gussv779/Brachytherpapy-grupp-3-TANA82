import json

import streamlit.components.v1 as components


def points_chart(df_all):
    source = df_all[["X_mm", "Y_mm", "Z_mm", "StructureName", "Type"]].dropna().to_dict(orient="records")

    structures = ['Urethra', 'Prostata', 'Rectum', 'Normalvävnad', 'Dröjpunkt']
    datasets = [{"dimensions": ["X_mm", "Y_mm", "Z_mm", "StructureName", "Type"], "source": source}]
    for s in structures:
        datasets.append({
            "transform": {"type": "filter", "config": {"dimension": "StructureName", "=": s}}
        })

    series = []
    for i, s in enumerate(structures, start=1):
        series.append({
            "name": s,
            "type": "scatter3D",
            "datasetIndex": i,
            "symbolSize": 3,
            "encode": {
                "x": "X_mm",
                "y": "Y_mm",
                "z": "Z_mm",
                "tooltip": ["StructureName", "Type", "X_mm", "Y_mm", "Z_mm"],
            }
        })

    option = {
        "tooltip": {},
        "legend": {"type": "scroll"},
        "grid3D": {"axisPointer": {"show": True}},
        "xAxis3D": {"type": "value", "name": "X (mm)"},
        "yAxis3D": {"type": "value", "name": "Y (mm)"},
        "zAxis3D": {"type": "value", "name": "Z (mm)"},
        "dataset": datasets,
        "series": series,
    }

    html = f"""
    <div style="display:flex; justify-content:center;">
      <div id="chart" style="width:50%;height:700px;"></div>
      <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/echarts-gl@2/dist/echarts-gl.min.js"></script>
      <script>
        const chart = echarts.init(document.getElementById('chart'));
        const option = {json.dumps(option)};

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
      </script>
    </div>
    """
    components.html(html, height=720, scrolling=False)