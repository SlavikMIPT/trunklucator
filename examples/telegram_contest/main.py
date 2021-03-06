import sys
import json
import codecs
import trunklucator
from jinja2 import Template


#You can change this format in frontend part.
#Current format - (label text, returning value, key code for shortcut)
#Use https://keycode.info/ to get key codes
META = {"buttons":[
        ('society (a)', 'society', 65), 
        ('economy (s)', 'economy', 83), 
        ('technology (d)', 'technology', 68), 
        ('sports (f)', 'sports', 70), 
        ('entertainment (h)', 'entertainment', 72), 
        ('science (j)', 'science', 74), 
        ('other (k)', 'other', 75),
        ('Skip (enter)', '', 13),
        ]}


HTML_TEMPLATE = '''
<style type="text/css">
</style>
<div class="columns is-centered content">
    <div class="column is-half">
    <table class="table is-bordered">
      {% for field in fields %}
      <tr>
        <td class="tg-0pky">{{ field }}</td>
        <td class="tg-0pky">{{ data[field] }}</td>
      </tr>
      {% endfor %}
    </table>
    </div>
</div>
'''

template = Template(HTML_TEMPLATE)

filter_fields = set(["article:published_time", "lang", "filename"])

with trunklucator.WebUI(data_dir="./data") as tru: # start http server in background
    for data in map(json.loads, sys.stdin): #read json data from standart input
        fields = [k for k in data.keys() if k not in filter_fields]
        data["label"] = tru.ask({"html": template.render(fields=fields, data=data)}, META)
        print("{}".format(json.dumps(data, ensure_ascii=False)), flush=True) #output result