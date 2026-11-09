from pathlib import Path
import re

src=Path("index V-1296.html")
dst=Path("index V-1297.html")
text=src.read_text(encoding="utf-8")
if "<title>Simulateur technique EVO-Sun — V1296</title>" not in text:
    raise SystemExit("Base V1296 non trouvée")

text=re.sub(r"(?<!\\d)V1296(?!\\d)","V1297",text)

old="""  function renderVictronCatalogDiagnostic(result={}){
    const box=document.getElementById('victronCatalogDiagnostic'),
      body=document.getElementById('victronCatalogDiagnosticBody');
    if(!box||!body)return;
    const tested=Array.isArray(result?.testedEndpoints)?result.testedEndpoints:[],
      candidates=Array.isArray(result?.candidateEndpoints)?result.candidateEndpoints:[];
    box.hidden=false;"""
new=old+"\n    box.open=false;"
if old not in text:
    raise SystemExit("Bloc diagnostic introuvable")
text=text.replace(old,new,1)
text=text.replace('<summary>Diagnostic E-Order</summary>','<summary>Diagnostic technique E-Order</summary>',1)

bt=chr(96)
dlr=chr(36)

pattern=r"""    }catch\(error\)\{
      await loadVictronCatalog\(\{silent:true\}\)\.catch\(\(\)=>\{\}\);
      if\(notice\)\{
        notice\.textContent=.*?
      \}
      renderVictronCatalogDiagnostic\(\{
        testedEndpoints,
        diagnostic:.*?
      \}\);
    }finally\{"""

new_lines=[
"    }catch(error){",
"      await loadVictronCatalog({silent:true}).catch(()=>{});",
"      const message=String(error?.message||error||''),",
"        paginationIssue=/pagination|offset|403|page suivante/i.test(message),",
"        kept=victronCatalogCache.length.toLocaleString('fr-BE');",
"      if(notice){",
"        notice.textContent=paginationIssue",
"          ?"+bt+"Catalogue Victron disponible : "+dlr+"{kept} référence"+dlr+"{victronCatalogCache.length>1?'s':''}. Mise à jour partielle : E-Order n’a pas fourni de page suivante exploitable. Les données existantes ont été conservées."+bt,
"          :"+bt+"Catalogue Victron disponible : "+dlr+"{kept} référence"+dlr+"{victronCatalogCache.length>1?'s':''}. La dernière tentative de mise à jour n’a pas pu être terminée ; les données existantes ont été conservées."+bt+";",
"      }",
"      renderVictronCatalogDiagnostic({",
"        testedEndpoints,",
"        diagnostic:paginationIssue?"+bt+"Mise à jour partielle. Le catalogue existant a été conservé. Détail technique : "+dlr+"{message}"+bt+":message",
"      });",
"    }finally{"
]
newcatch="\n".join(new_lines)
text,count=re.subn(pattern,newcatch,text,count=1,flags=re.S)
if count!=1:
    raise SystemExit("Catch synchronisation introuvable")

old_rate="Victron E-Order applique une limitation de débit."
if old_rate in text:
    text=text.replace(
        old_rate,
        "Catalogue Victron disponible : ",
        1
    )

css="""
/* V1297 — diagnostic E-Order secondaire et fermé par défaut. */
.victron-catalog-diagnostic summary::after{content:" · ouvrir uniquement pour le diagnostic technique";font-size:10px;font-weight:700;color:#71808a}
.victron-catalog-diagnostic[open] summary::after{content:" · diagnostic affiché"}
"""
p=text.find('<style id="v1187BundledStyles">')
q=text.find('</style>',p)
if p<0 or q<0:
    raise SystemExit("Style introuvable")
text=text[:q]+css+"\n"+text[q:]

required=[
"<title>Simulateur technique EVO-Sun — V1297</title>",
"Catalogue Victron disponible",
"Mise à jour partielle",
"box.open=false",
"Diagnostic technique E-Order"
]
missing=[x for x in required if x not in text]
if missing:
    raise SystemExit("Validation V1297: "+repr(missing))
if not text.rstrip().endswith("</html>"):
    raise SystemExit("HTML incomplet")

dst.write_text(text,encoding="utf-8")
print("Créé",dst,dst.stat().st_size)
