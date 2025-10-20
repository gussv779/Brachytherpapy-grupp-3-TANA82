import json
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

def lpm_chart(P_dose):

    st.subheader("Dose Optimization")

    data = P_dose[["X_mm", "Y_mm", "Z_mm", "Dose", "StructureName"]].to_records(index=False).tolist()

    dose_min = float(np.nanmin(P_dose["Dose"])) if len(P_dose) else 0.0
    dose_max = float(np.nanmax(P_dose["Dose"])) if len(P_dose) else 1.0
    if dose_max <= dose_min:
        dose_max = dose_min + 1e-6

    p5, p95 = np.percentile(P_dose["Dose"], [5, 95]) if len(P_dose) else (0.0, 1.0)
    vm_min = float(min(dose_min, p5))
    vm_max = float(max(dose_max, p95))
    if vm_max <= vm_min:
        vm_max = vm_min + 1e-6

    html = f"""
    <style>
      .chart-panel {{
        width: 720px;
        max-width: 50%;
        border: 1px solid #3a3a3a;   /* border */
        border-radius: 10px;         /* rounded corners */
        padding: 12px;               /* space between border and chart */
        box-shadow: 0 6px 18px rgba(0,0,0,0.12);
        background: rgba(255,255,255,0.02);
      }}
      .chart-fill {{
        width: 100%;
        height: 680px;               /* inner chart height */
      }}
      @media (max-width: 900px) {{
        .chart-panel {{ max-width: 100%; width: 100%; }}
      }}
    </style>

    <div style="display:flex; justify-content:center;">
      <div class="chart-panel">
        <div id="dose3d" class="chart-fill"></div>
      </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts-gl@2/dist/echarts-gl.min.js"></script>
    <script>
      const chart = echarts.init(document.getElementById('dose3d'));
      const option = {{
        tooltip: {{
          formatter: function (p) {{
            const v = p.value;
            return 'X: ' + v[0].toFixed(1) + ' mm'
                 + '<br/>Y: ' + v[1].toFixed(1) + ' mm'
                 + '<br/>Z: ' + v[2].toFixed(1) + ' mm'
                 + '<br/><b>Dose: ' + v[3].toPrecision(4) + '</b>'
                 + (v[4] ? '<br/>Structure: ' + v[4] : '');
          }}
        }},
        visualMap: {{
          type: 'continuous',
          dimension: 3,
          min: {vm_min},
          max: {vm_max},
          calculable: true,
          orient: 'vertical',
          left: 'left',
          inRange: {{
            color: [
              '#313695','#4575b4','#74add1','#abd9e9','#e0f3f8',
              '#ffffbf','#fee090','#fdae61','#f46d43','#d73027','#a50026'
            ],
            colorAlpha: [0.9, 1.0],
            symbolSize: [2, 12]
          }}
        }},
        grid3D: {{
          axisLine: {{ lineStyle: {{ color: '#666' }} }},
          axisPointer: {{ lineStyle: {{ color: '#999' }} }},
          splitLine: {{ show: true, lineStyle: {{ color: '#555', opacity: 0.25 }} }},
          viewControl: {{ projection: 'orthographic' }}
        }},
        xAxis3D: {{ type: 'value', name: 'X (mm)' }},
        yAxis3D: {{ type: 'value', name: 'Y (mm)' }},
        zAxis3D: {{ type: 'value', name: 'Z (mm)' }},
        series: [{{
          type: 'scatter3D',
          symbolSize: {3},
          data: {json.dumps(data)},
          dimensions: ['X_mm','Y_mm','Z_mm','Dose','Structure'],
          encode: {{ x: 0, y: 1, z: 2, tooltip: [0,1,2,3,4] }}
        }}]
      }};
      chart.setOption(option);
      window.addEventListener('resize', () => chart.resize());
    </script>
    """
    components.html(html, height=750, scrolling=False)
