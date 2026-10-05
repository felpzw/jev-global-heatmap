"""Compare renderer construction and export a browser benchmark without LLM calls.

Run from the repository root: python benchmark_map.py --baseline-ref ab78177
Only execute trusted local revisions: the baseline module is loaded as Python code.
"""

import argparse
import json
from pathlib import Path
import platform
from statistics import median
import subprocess
from time import perf_counter
import types

import plotly
from plotly.offline import get_plotlyjs
import pycountry

from src.components.map_renderer import plot_heatmap


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default="ab78177")
    parser.add_argument("--repeats", type=int, default=30)
    parser.add_argument("--output", type=Path, default=Path("artifacts/redesign"))
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be positive")
    baseline = types.ModuleType("baseline")
    source = subprocess.check_output(
        ["git", "show", f"{args.baseline_ref}:src/components/map_renderer.py"], text=True,
    )
    exec(compile(source, "baseline_renderer.py", "exec"), baseline.__dict__)
    fixtures = {
        "demo": json.loads(Path("data/demo_heatmap.json").read_text())["countries"],
        "large": [
            {"iso_alpha_3": country.alpha_3, "heat_score": index % 101,
             "context_summary": "Amostra sintética de desempenho; sem valor factual."}
            for index, country in enumerate(sorted(pycountry.countries, key=lambda c: c.alpha_3))
        ],
    }
    report = {
        "platform": platform.platform(), "python": platform.python_version(),
        "plotly": plotly.__version__, "baseline_ref": args.baseline_ref,
        "repeats": args.repeats, "warmups": 3, "cases": {},
        "scope": "Python construction + serialization; browser timing is measured separately in benchmark.html",
    }
    figures = {}
    renderers = {"before": baseline.plot_heatmap, "after": plot_heatmap}
    for name, data in fixtures.items():
        samples = {version: [] for version in renderers}
        for index in range(args.repeats + 3):
            order = list(renderers) if index % 2 == 0 else list(reversed(renderers))
            for version in order:
                start = perf_counter()
                figure = renderers[version](data)
                serialized = figure.to_json()
                elapsed = (perf_counter() - start) * 1000
                if index >= 3:
                    samples[version].append(elapsed)
                figures[f"{name}_{version}"] = json.loads(serialized)
        report["cases"][name] = {
            "countries": len(data),
            **{version: {"median_ms": round(median(values), 3),
                         "samples_ms": [round(v, 3) for v in values],
                         "json_bytes": len(json.dumps(figures[f"{name}_{version}"]).encode())}
               for version, values in samples.items()},
        }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "python.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.output / "plotly.min.js").write_text(get_plotlyjs())
    payload = json.dumps(figures).replace("<", "\\u003c")
    html = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>JEV · comparação do mapa</title>
<style>body{font:16px system-ui;margin:24px;background:#fff;color:#17212f}
body.dark{background:#0e1117;color:#fafafa}button{padding:10px;margin:4px}
.grid{display:flex;flex-wrap:wrap;gap:24px}.panel{flex:1;min-width:280px}
.chart{width:100%}pre{white-space:pre-wrap}body.mobile .panel{flex:none;width:320px}</style>
<h1>Comparação do mapa · dados fictícios</h1>
<button onclick="document.body.classList.toggle('dark');resize()">Tema claro/escuro</button>
<button onclick="document.body.classList.toggle('mobile');resize()">Largura de 320 px</button>
<button id="run" onclick="run()">Medir renderização e atualização</button>
<p>8 e 249 países. CDN de geometrias necessário no primeiro carregamento.
O benchmark aquece cada caso uma vez e alterna a ordem em 10 repetições.
Inclui Plotly.newPlot e Plotly.react com mudança de scores; não mede FPS nem LLM.</p>
<div class="grid"><section class="panel"><h2>Antes</h2><div id="before" class="chart"></div></section>
<section class="panel"><h2>Depois</h2><div id="after" class="chart"></div></section></div>
<pre id="output">Pronto para medir.</pre><script src="plotly.min.js"></script><script>
const figures = PAYLOAD;
const config = {responsive:true, scrollZoom:false, displaylogo:false};
const fresh = key => JSON.parse(JSON.stringify(figures[key]));
function resize(){for(const id of ['before','after']) Plotly.Plots.resize(id)}
async function show(){for(const version of ['before','after']) {
 const f=fresh('demo_'+version);await Plotly.newPlot(version,f.data,f.layout,config)}}
const frame = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
async function measure(version,fixture){
 const f=fresh(fixture+'_'+version);Plotly.purge(version);
 let start=performance.now();await Plotly.newPlot(version,f.data,f.layout,config);await frame();
 const render=performance.now()-start;
 const next=fresh(fixture+'_'+version);
 // Baseline Express may serialize z as a typed-array envelope; use matching plain values.
 next.data[0].z=Array.from(figures[fixture+'_after'].data[0].z,z=>100-z);
 next.layout.uirevision='updated';if(next.layout.geo)next.layout.geo.uirevision='updated';
 start=performance.now();await Plotly.react(version,next.data,next.layout,config);await frame();
 return {render_ms:render,update_ms:performance.now()-start};
}
async function run(){
 document.getElementById('run').disabled=true;
 const out=document.getElementById('output');out.textContent='Medição em andamento…';
 try {
 const report={browser:navigator.userAgent,viewport:[innerWidth,innerHeight],
 chart_width:document.getElementById('after').clientWidth,repeats:10,cases:{}};
 for(const fixture of ['demo','large']){
 const samples={before:[],after:[]};
 for(let i=-1;i<10;i++)for(const version of (i%2===0?['before','after']:['after','before'])){
 const sample=await measure(version,fixture);if(i>=0)samples[version].push(sample)}
 const med=a=>{a.sort((a,b)=>a-b);return (a[4]+a[5])/2};
 report.cases[fixture]=Object.fromEntries(Object.entries(samples).map(([v,s])=>[v,{
 render_ms:med(s.map(x=>x.render_ms)),update_ms:med(s.map(x=>x.update_ms))}]));
 }
 out.textContent=JSON.stringify(report,null,2);
 }catch(e){out.textContent='Falha: '+e.message}finally{document.getElementById('run').disabled=false;await show()}
}
show();</script></html>'''.replace("PAYLOAD", payload)
    (args.output / "benchmark.html").write_text(html)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
