;jQuery.fn.extend({getUrlParam(strParamName){let qString,strHref,strQueryString;strParamName=escape(unescape(strParamName));if($(this).attr("nodeName")==="#document"){if(window.location.search.search(strParamName)>-1){qString=window.location.search.substr(1,window.location.search.length).split("&");}}else if($(this).attr("src")!=="undefined"){strHref=$(this).attr("src");if(strHref.indexOf("?")>-1){strQueryString=strHref.substr(strHref.indexOf("?")+1);qString=strQueryString.split("&");}}else if($(this).attr("href")!=="undefined"){strHref=$(this).attr("href");if(strHref.indexOf("?")>-1){strQueryString=strHref.substr(strHref.indexOf("?")+1);qString=strQueryString.split("&");}}else{return null;}
if(!qString){return null;}
let returnVal=(Array.from(qString).filter((query)=>escape(unescape(query.split("=")[0]))===strParamName).map((query)=>query.split("=")[1]));if(returnVal.lenght===0){return null;}else if(returnVal.lenght===1){return returnVal[0];}else{return returnVal;}}});;window.load_start=Date.now();$(window).on('load',()=>window.time_load_ms=+(Date.now()-window.load_start));$(function(){let mt_reject_impl;let mt_submit_ready=false;window.mt_submit_ready=function(data_callback){if(!mt_submit_ready){mt_submit_ready=true;let btn=$('#btn-submit').removeAttr('disabled');let btn_rej=$('#btn-reject').removeAttr('disabled');if(data_callback!=null){btn.on('click',window.mt_submit(data_callback));btn_rej.on('click',window.mt_reject(data_callback));}}};window.mt_submit_not_ready=function(disable){if(disable==null){disable=true;}
if(mt_submit_ready){mt_submit_ready=false;if(disable){$('#btn-submit').attr('disabled','disabled').off('click');}
if(disable){$('#btn-reject').attr('disabled','disabled').off('click');}}};window.mt_submit=function(data_callback){mt_submit_ready=true;let do_submit=mt_submit_impl(data_callback);do_submit();};window.mt_reject=function(data_callback){mt_submit_ready=true;let do_submit=mt_reject_impl(data_callback);do_submit();};window.mt_submit_partial=function(data){console.log("partial submit data:");console.log(data);return $.ajax({type:'POST',url:window.location.href,data:$.extend(true,{partial:true,screen_width:screen.width,screen_height:screen.height,time_load_ms:window.time_load_ms},data),contentType:'application/x-www-form-urlencoded; charset=UTF-8',dataType:'json',success(data,status,jqxhr){console.log("partial submit success: data:");return console.log(data);},error(){return console.log("partial submit error");}});};let mt_submit_error=msg=>hide_modal_loading(()=>window.show_modal_error(msg));var mt_submit_impl=data_callback=>function(){if(!mt_submit_ready){return;}
let data=data_callback();window.show_modal_loading("Submitting...",0);return $.ajax({type:'POST',url:window.location.href,data:$.extend(true,{screen_width:screen.width,screen_height:screen.height,accepted:true,time_load_ms:window.time_load_ms},data),contentType:'application/x-www-form-urlencoded; charset=UTF-8',dataType:'json',success(data,status,jqxhr){let new_url=`/via_image/`;if(data.result==="success"){window.location=new_url;setInterval((()=>window.location=new_url),5000);}else if(data.result==="error"){mt_submit_error(`There was an error contacting the server;try submitting again after a few seconds...(${data.message})`);}else{mt_submit_error("There was an error contacting the server; try submitting again after a few seconds...");}},error(){mt_submit_error("Could not connect to the server; try submitting again after a few seconds...");}});};return mt_reject_impl=data_callback=>function(){if(!mt_submit_ready){return;}
let data=data_callback();window.show_modal_loading("Submitting...",0);return $.ajax({type:'POST',url:window.location.href,data:$.extend(true,{screen_width:screen.width,screen_height:screen.height,accepted:false,time_load_ms:window.time_load_ms},data),contentType:'application/x-www-form-urlencoded; charset=UTF-8',dataType:'json',success(data,status,jqxhr){let new_url=`/via_image/question_review/${window.template_args.photo_id}`;if(data.result==="success"){window.location=new_url;return setInterval((()=>window.location=new_url),5000);}else if(data.result==="error"){return mt_submit_error(`There was an error contacting the server;try submitting again after a few seconds...(${data.message})`);}else{return mt_submit_error("There was an error contacting the server; try submitting again after a few seconds...");}},error(){mt_submit_error("Could not connect to the server; try submitting again after a few seconds...");}});};});;$(function(){template_args.width=$("#mt-image").width();template_args.height=(720/1280)*$('#mt-image').width();template_args.container_id='mt-image';$('#poly-container').width(template_args.width).height(template_args.height);});let btn_submit=()=>window.mt_submit(window.controller_ui.get_submit_data);let btn_reject=()=>window.mt_reject(window.controller_ui.get_submit_data);$(window).on('load',function(){$('#btn-submit').on('click',btn_submit);$('#btn-reject').on('click',btn_reject);});