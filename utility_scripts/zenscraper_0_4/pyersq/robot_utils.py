<<<<<<< HEAD
"""Common functions for robots. """
import os
from datetime import datetime
from pathlib import Path

IDX_HTML=  r"""
<!DOCTYPE html>
<html lang="en"><meta charset="UTF-8"><head>
<style type="text/css">
a:link {color:#0000FF;}
a:visited {color:#FF00FF;}
a:hover {color:#FF0000;}
a:active{color:#FF0000;}
span, a {text-decoration:none; font-size:14px; font-family:arial; font-weight:bold; margin-left:15px; white-space:nowrap;}
.a1 {text-decoration:none; margin-left:30px; font-size:12px; font-family:arial; font-weight:normal; white-space:nowrap;}
#Main,.toggle {color:#269; font-weight:bold;
font-family:Arial,FreeSans,Helvetica,sans-serif; font-size:12px; white-space:nowrap;
padding-left: 0em; margin-left:5em;}
#Main li {list-style: none; text-index: -.5em;}
li .menu_label + input[type=checkbox] {opacity: 100;}
li .menu_label {cursor: pointer; margin-left:-2em;}
li .menu_label + input[type=checkbox] + ol > li {display:none;}
li .menu_label + input[type=checkbox]:checked + ol > li {display:block; margin-left:-1em;}
.alink {text-decoration:none; margin-left:-3em; font-weight:bold;
font-family:Arial,FreeSans,Helvetica,sans-serif; font-size:12px;}
table {border-collapse:collapse; width:99%; height:98%; position:fixed; top:5px; bottom:5px; left:5px; right:5px; border:1; cellspacing:2; cellpadding:2;}
table, th, td {border: 1px solid green;}
input{float:left; margin-left:-3.5em; margin-top:-0.1em;}
.toggle {text-decoration:none; margin-left:3em}
#leftNav {height:96%; overflow:visible; vertical-align:top; width:25%;}
#rbdNavMenu {width:98%; height:96%; overflow:auto; position:inherit; background-color:#f5f5f5; border-radius:4px; box-shadow:inset 0 1px 1px rgba(0, 0, 0, 0.05); margin:5px;}
#mainTree{background-color:#f5f5f5; border-radius:4px; box-shadow:inset 0 1px 1px rgba(0, 0, 0, 0.05); margin:5px; text-align:center; width:98%;}
</style>
<script>
function checkAll(checkToggle){
    var checkboxes = new Array();
    checkboxes = document.getElementsByTagName('input');

    for (var i=0; i<checkboxes.length; i++){
        if (checkboxes[i].type == 'checkbox'){
            checkboxes[i].checked = checkToggle;
        }
    }

}
</script>
</head>
<body onload="javascript:displayMenuNav(); return false;">
<table>
    <tr height="20px">
        <td valign="top" align="center" colspan="2" style="font-weight:bold; font-family:Arial,FreeSans,Helvetica,sans-serif; font-size:20px; background-color:yellow;">
            Index
        </td>
    </tr>
    <tr>
        <td valign="top" width="25%" id="leftNav">
            <div style="width: 100%; height:98%; overflow:auto; " id="navMenu">
                <idx_js_for_menu>
            </div>
        </td>
        <td valign="top">
            <iframe name="a" frameborder="0" height="500%" width="100%"/>
        </td>
    </tr>
</table>
</body>
</html>
"""

IDX_JS_FOR_MENU = r"""
<script type="text/javascript">
    var text = '<navtree>';
    var results = eval("(" + text + ")");
    var ol, li, idRegEx;
    var htmlData="";
    var id="";
    var prevId="";
    var type=".<filetype>"
    var ctr=0;

    document.getElementById("leftNav").innerHTML='<div id="mainTree">\n' +
        '    <a onclick="javascript:checkAll(true);" href="javascript:void();" class="toggle">Expand All</a>\n' +
        '    <a onclick="javascript:checkAll(false);" href="javascript:void();" class="toggle">Collapse All</a>\n' +
        '</div>\n' +
        '<div style="width:100%; height:780px; overflow:auto; "><ol id="Main"></ol>\n' +
        '</div>'
    try{
        for (i in results){
            var obj = results[i];
            id="";
            prevId="";

            for(prop in obj) {
                if (prop.indexOf("Category") > -1) {
                    id = id + obj[prop];
                    prevId = id;
                    htmlData = document.getElementById(id);

                    if (htmlData == undefined || htmlData == null) {
                        ctr = ctr + 1;

                        if (prop == "Category1") {
                            htmlData = document.getElementById("Main");
                            createElem(htmlData, obj[prop], ctr, obj[prop], 1)
                        } else {
                            idRegEx = new RegExp(obj[prop].replace(/[!@#$%^&*()+=\-[\]\\';,./{}|":<>?~_]/g, "\\&") + '$')
                            htmlData = document.getElementById(id.replace(idRegEx, ""))
                            createElem(htmlData, id, ctr, obj[prop], 2)
                        }
                    }
                }
                if (prop.indexOf("PageNum") > -1) {
                    htmlData = document.getElementById(prevId);
                    createLink(htmlData.results[i].ObjectKey, results[i].PageNum)
                }
            }
        }
    } catch(err) {
        htmlData = document.getElementById("Main");
        if(htmlData!="" && htmlData!=undefined && htmlData!= null){
            htmlData.innerHTML = '<li>Ooops! An error has occured! ('+ err.message +')';
        }else {
            htmlData = document.createElement("ol");
            htmlData.id = "Main"
            htmlData.innerHTML = 'Ooops! An error has occured! ('+ err.message +')'
        }
        document.getElementsByTagName("body")[0].appendChild(htmlData)
    }
    
    function createLink(htmlData, id, pageNum){
        li = document.createElement('li');
        li.className = "page";
        li.innerHTML = '<a href="'+id+type+'" target="a" class="alink">Page '+pageNum+'</a>';
        htmlData.childNodes[2].appendChild(li)
    }
    
    function createElem(htmlData, id, ctr, txt, nodeNum){
        li = document.createElement("li");
        li.id = id;
        li.innerHTML = '<label class="menu_label" for="a'+ctr+'">'+txt+'</label><input type="checkbox" id="a'+ctr+'" checked \/>';
        ol = document.createElement("ol");
        htmlData.appendChild(ol);
        li.appendChild(ol);
        try{
            htmlData.childNodes[nodeNum].appendChild(li);
        }catch(err){
            htmlData.appendChild(li);
        }
    }
</script>
"""

def save_output(df, outdir, filename, fileext="csv"):
    """
    Create a file to contain output. If it already exists, create a backup first.
    :param df: Dataframe to export
    :param outdir: folder to save output
    :param filename: str
    :param fileext: Extension of output file; default is 'csv'
    :return:
    """
    outfile = f"{outdir}{filename}"
    if Path(f"{outfile}.{fileext}").is_file():
        # file exists, need to backup
        suffix = "backup" + datetime.now().strftime("_%H_%M_%S")
        os.rename(f"{outfile}.{fileext}", f"{outfile}_{suffix}_{fileext}")

    if fileext == "csv":
        df.to_csv(f"{outfile}.csv", encoding="utf-8")

def multiline_string_to_dict(string):
    """
    Convert a string to a dictionary.
    Useful when converting header strings copied from the browser development tools, for example:

    Content-Encoding ; gzip
    Content-Type = text/html; charset-utf-8
    Server: cloudfare
    Transfer-Encoding: chunked
    Vary: Accept-Encoding
    Via: kong/2.0.2, 1.1 rrinbvgw44
    """

    keys, values = list(), list()
    for line in string.strip().split("\n"):
        s1, s2 = line.split(":", 1)
        keys.append(s1.strip())
        values.append(s2.strip())
    return dict(zip(keys, values))

def create_index(df, htmldir, filetype="html", **kwargs):
    """
    Create an HTML index to allow easy referencing of scraped files
    :param df:
    :param htmldir:
    :param filetype:
    :param kwargs:
    :return:
    """
    columns = ["ObjectKey"]
    rename = {}
    sort = []
    for key, val in kwargs.items():
        key = key.replace("cat", 'Category')
        columns.append(val)
        rename[val] = key
        sort.append(key)
    columns.append("PageNum")
    sort.append("PageNum")

    df = df[columns]
    df = df.rename(columns=rename)
    df = df.sort_values(by=sort)
    navtree = df.to_dict(orient='records')

    str_navtree = str(navtree).replace("'", "\"")
    js = IDX_JS_FOR_MENU.replace("<navtree>", str_navtree).replace("<filepat>", filetype)
    html = IDX_HTML.replace("<idx_js_for_menu>", js)
    with open(f"{htmldir}index.html","w",encoding="utf-8") as f:
=======
"""Common functions for robots. """
import os
from datetime import datetime
from pathlib import Path

IDX_HTML=  r"""
<!DOCTYPE html>
<html lang="en"><meta charset="UTF-8"><head>
<style type="text/css">
a:link {color:#0000FF;}
a:visited {color:#FF00FF;}
a:hover {color:#FF0000;}
a:active{color:#FF0000;}
span, a {text-decoration:none; font-size:14px; font-family:arial; font-weight:bold; margin-left:15px; white-space:nowrap;}
.a1 {text-decoration:none; margin-left:30px; font-size:12px; font-family:arial; font-weight:normal; white-space:nowrap;}
#Main,.toggle {color:#269; font-weight:bold;
font-family:Arial,FreeSans,Helvetica,sans-serif; font-size:12px; white-space:nowrap;
padding-left: 0em; margin-left:5em;}
#Main li {list-style: none; text-index: -.5em;}
li .menu_label + input[type=checkbox] {opacity: 100;}
li .menu_label {cursor: pointer; margin-left:-2em;}
li .menu_label + input[type=checkbox] + ol > li {display:none;}
li .menu_label + input[type=checkbox]:checked + ol > li {display:block; margin-left:-1em;}
.alink {text-decoration:none; margin-left:-3em; font-weight:bold;
font-family:Arial,FreeSans,Helvetica,sans-serif; font-size:12px;}
table {border-collapse:collapse; width:99%; height:98%; position:fixed; top:5px; bottom:5px; left:5px; right:5px; border:1; cellspacing:2; cellpadding:2;}
table, th, td {border: 1px solid green;}
input{float:left; margin-left:-3.5em; margin-top:-0.1em;}
.toggle {text-decoration:none; margin-left:3em}
#leftNav {height:96%; overflow:visible; vertical-align:top; width:25%;}
#rbdNavMenu {width:98%; height:96%; overflow:auto; position:inherit; background-color:#f5f5f5; border-radius:4px; box-shadow:inset 0 1px 1px rgba(0, 0, 0, 0.05); margin:5px;}
#mainTree{background-color:#f5f5f5; border-radius:4px; box-shadow:inset 0 1px 1px rgba(0, 0, 0, 0.05); margin:5px; text-align:center; width:98%;}
</style>
<script>
function checkAll(checkToggle){
    var checkboxes = new Array();
    checkboxes = document.getElementsByTagName('input');

    for (var i=0; i<checkboxes.length; i++){
        if (checkboxes[i].type == 'checkbox'){
            checkboxes[i].checked = checkToggle;
        }
    }

}
</script>
</head>
<body onload="javascript:displayMenuNav(); return false;">
<table>
    <tr height="20px">
        <td valign="top" align="center" colspan="2" style="font-weight:bold; font-family:Arial,FreeSans,Helvetica,sans-serif; font-size:20px; background-color:yellow;">
            Index
        </td>
    </tr>
    <tr>
        <td valign="top" width="25%" id="leftNav">
            <div style="width: 100%; height:98%; overflow:auto; " id="navMenu">
                <idx_js_for_menu>
            </div>
        </td>
        <td valign="top">
            <iframe name="a" frameborder="0" height="500%" width="100%"/>
        </td>
    </tr>
</table>
</body>
</html>
"""

IDX_JS_FOR_MENU = r"""
<script type="text/javascript">
    var text = '<navtree>';
    var results = eval("(" + text + ")");
    var ol, li, idRegEx;
    var htmlData="";
    var id="";
    var prevId="";
    var type=".<filetype>"
    var ctr=0;

    document.getElementById("leftNav").innerHTML='<div id="mainTree">\n' +
        '    <a onclick="javascript:checkAll(true);" href="javascript:void();" class="toggle">Expand All</a>\n' +
        '    <a onclick="javascript:checkAll(false);" href="javascript:void();" class="toggle">Collapse All</a>\n' +
        '</div>\n' +
        '<div style="width:100%; height:780px; overflow:auto; "><ol id="Main"></ol>\n' +
        '</div>'
    try{
        for (i in results){
            var obj = results[i];
            id="";
            prevId="";

            for(prop in obj) {
                if (prop.indexOf("Category") > -1) {
                    id = id + obj[prop];
                    prevId = id;
                    htmlData = document.getElementById(id);

                    if (htmlData == undefined || htmlData == null) {
                        ctr = ctr + 1;

                        if (prop == "Category1") {
                            htmlData = document.getElementById("Main");
                            createElem(htmlData, obj[prop], ctr, obj[prop], 1)
                        } else {
                            idRegEx = new RegExp(obj[prop].replace(/[!@#$%^&*()+=\-[\]\\';,./{}|":<>?~_]/g, "\\&") + '$')
                            htmlData = document.getElementById(id.replace(idRegEx, ""))
                            createElem(htmlData, id, ctr, obj[prop], 2)
                        }
                    }
                }
                if (prop.indexOf("PageNum") > -1) {
                    htmlData = document.getElementById(prevId);
                    createLink(htmlData.results[i].ObjectKey, results[i].PageNum)
                }
            }
        }
    } catch(err) {
        htmlData = document.getElementById("Main");
        if(htmlData!="" && htmlData!=undefined && htmlData!= null){
            htmlData.innerHTML = '<li>Ooops! An error has occured! ('+ err.message +')';
        }else {
            htmlData = document.createElement("ol");
            htmlData.id = "Main"
            htmlData.innerHTML = 'Ooops! An error has occured! ('+ err.message +')'
        }
        document.getElementsByTagName("body")[0].appendChild(htmlData)
    }
    
    function createLink(htmlData, id, pageNum){
        li = document.createElement('li');
        li.className = "page";
        li.innerHTML = '<a href="'+id+type+'" target="a" class="alink">Page '+pageNum+'</a>';
        htmlData.childNodes[2].appendChild(li)
    }
    
    function createElem(htmlData, id, ctr, txt, nodeNum){
        li = document.createElement("li");
        li.id = id;
        li.innerHTML = '<label class="menu_label" for="a'+ctr+'">'+txt+'</label><input type="checkbox" id="a'+ctr+'" checked \/>';
        ol = document.createElement("ol");
        htmlData.appendChild(ol);
        li.appendChild(ol);
        try{
            htmlData.childNodes[nodeNum].appendChild(li);
        }catch(err){
            htmlData.appendChild(li);
        }
    }
</script>
"""

def save_output(df, outdir, filename, fileext="csv"):
    """
    Create a file to contain output. If it already exists, create a backup first.
    :param df: Dataframe to export
    :param outdir: folder to save output
    :param filename: str
    :param fileext: Extension of output file; default is 'csv'
    :return:
    """
    outfile = f"{outdir}{filename}"
    if Path(f"{outfile}.{fileext}").is_file():
        # file exists, need to backup
        suffix = "backup" + datetime.now().strftime("_%H_%M_%S")
        os.rename(f"{outfile}.{fileext}", f"{outfile}_{suffix}_{fileext}")

    if fileext == "csv":
        df.to_csv(f"{outfile}.csv", encoding="utf-8")

def multiline_string_to_dict(string):
    """
    Convert a string to a dictionary.
    Useful when converting header strings copied from the browser development tools, for example:

    Content-Encoding ; gzip
    Content-Type = text/html; charset-utf-8
    Server: cloudfare
    Transfer-Encoding: chunked
    Vary: Accept-Encoding
    Via: kong/2.0.2, 1.1 rrinbvgw44
    """

    keys, values = list(), list()
    for line in string.strip().split("\n"):
        s1, s2 = line.split(":", 1)
        keys.append(s1.strip())
        values.append(s2.strip())
    return dict(zip(keys, values))

def create_index(df, htmldir, filetype="html", **kwargs):
    """
    Create an HTML index to allow easy referencing of scraped files
    :param df:
    :param htmldir:
    :param filetype:
    :param kwargs:
    :return:
    """
    columns = ["ObjectKey"]
    rename = {}
    sort = []
    for key, val in kwargs.items():
        key = key.replace("cat", 'Category')
        columns.append(val)
        rename[val] = key
        sort.append(key)
    columns.append("PageNum")
    sort.append("PageNum")

    df = df[columns]
    df = df.rename(columns=rename)
    df = df.sort_values(by=sort)
    navtree = df.to_dict(orient='records')

    str_navtree = str(navtree).replace("'", "\"")
    js = IDX_JS_FOR_MENU.replace("<navtree>", str_navtree).replace("<filepat>", filetype)
    html = IDX_HTML.replace("<idx_js_for_menu>", js)
    with open(f"{htmldir}index.html","w",encoding="utf-8") as f:
>>>>>>> 9c7a2ecb38c8c26c66a48d4e0105990ca3cfbfd4
        f.write(html)