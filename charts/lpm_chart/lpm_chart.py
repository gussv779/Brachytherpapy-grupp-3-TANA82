import json
import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from mock_dose_data import sample_dwell_times, make_mock_dij, compute_point_doses



def lpm_chart(P_dose):

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
    <div style="display:flex; justify-content:center;">
        <div id="dose3d" style="width:720px; max-width:50%; height:720px;"></div>
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
    </div>
    """
    components.html(html, height=750, scrolling=False)