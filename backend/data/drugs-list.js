var getUrlParameter = function getUrlParameter(sParam) {
	var sPageURL = window.location.search.substring(1),
		sURLVariables = sPageURL.split('&'),
		sParameterName,
		i;

	for (i = 0; i < sURLVariables.length; i++) {
		sParameterName = sURLVariables[i].split('=');

		if (sParameterName[0] === sParam) {
			return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
		}
	}

};


var url = window.location.pathname;
var urlmain = window.location.href;
url = url.split("/");
var lang = url[1];
var bas_url = document.location.origin;
var drugs_json = bas_url + "/GetDrugs.php";
var drugs_json_basic = bas_url + "/GetDrugs.php";
var searchjson = bas_url + "/GetDrugsSearch3.php?";
var drugs_json_search = "";
var registernumberjson = bas_url + "/GetDrugAgents.php?";
var drugs_json_registernumber = "";
var page_IsMax = "";
var nextpg = 0;
var prevpg = 0;
var reportFile = "";

if (getUrlParameter("pg") === undefined) {
	drugs_json = drugs_json+"?page=1" ;
} else {
	drugs_json += "?page=" + getUrlParameter("pg");
}
if(getUrlParameter("q") !== undefined){
   jQuery('#textInput').val(getUrlParameter("q"));
   }


jQuery(document).ready(function() {
	jQuery('#drugs_loading').show();
	var drugs_list_table = "";
	var count = "";
	var results = "";
  var TradeName = "";
  var ScientificName = "";
  var Agent = "";
  var ManufacturerName = "";
  var RegNo = "";
	

	if (getUrlParameter("pg") > 1) {
		jQuery('.prevbutton').css("display", "block");
		jQuery('.firstpage').css("display", "block");
	}
	jQuery('.paginations').hide();
	setTimeout( function(){ jQuery('.loader').css("display","none"); }  , 500 );
	
		drugs_list_table += '<thead><tr>';
		drugs_list_table += '<th>' + (lang == "en" ? "Scientific Name" : "الاسم العلمي") + '</th>';
		drugs_list_table += '<th>' + (lang == "en" ? "Trade Name" : "الاسم التجاري") + '</th>';
		drugs_list_table += '<th>' + (lang == "en" ? "Strength" : "التركيز") + '</th>';
		drugs_list_table += '<th>' + (lang == "en" ? "Doesage Form" : "الشكل الصيدلاني") + '</th>';
		// 	drugs_list_table += '<th>'+( lang == "en" ? "Underweight" : "الشركة المسوقة") +'</th>';
		drugs_list_table += '<th>' + (lang == "en" ? "Price" : "السعر") + '</th>';
		drugs_list_table += '<th>' + (lang == "en" ? "Details" : "التفاصيل") + '</th>';
		drugs_list_table += '</tr></thead>';
		drugs_list_table += '<tbody>';
  
  if(getUrlParameter("TradeName") !== undefined){
    TradeName = getUrlParameter("TradeName");
    jQuery('#TradeName').val(TradeName);
  }
    
  if(getUrlParameter("ScientificName") !== undefined){
    ScientificName = getUrlParameter("ScientificName");
    jQuery('#ScientificName').val(ScientificName);
  }

  if(getUrlParameter("Agent") !== undefined){
    Agent = getUrlParameter("Agent");
    jQuery('#Agent').val(Agent);
  }

  if(getUrlParameter("ManufacturerName") !== undefined){
    ManufacturerName = getUrlParameter("ManufacturerName");
    jQuery('#ManufacturerName').val(ManufacturerName);
  }

  if(getUrlParameter("RegNo") !== undefined){
    RegNo = getUrlParameter("RegNo");
    jQuery('#RegNo').val(RegNo);
  }
    
   
  if(TradeName !="" || ScientificName !="" || Agent !="" || ManufacturerName !="" || RegNo !=""){
	drugs_json_search = searchjson;
  var attrs="TradeName="+TradeName+"&ScientificName="+ScientificName+"&Agent="+Agent+"&ManufacturerName="+ManufacturerName+"&RegNo="+RegNo;
  
	drugs_json_search += attrs;
    if(getUrlParameter("pg") !== undefined){
   drugs_json_search +="&page=" + getUrlParameter("pg"); 
       }
    
  jQuery.getJSON(drugs_json_search, function(data) {
			results = data.results;
    if( results == null ){
			drugs_list_table += '<tr><td colspan="6"><h3 class="no-result">' + (lang == "en" ? "No Results Found" : " لا توجد نتائج ") + '</h3></td></tr>';
			drugs_list_table += '</tbody>';
			jQuery('#drugslisttable').html(drugs_list_table);
		}
		else{
    var countit = 1;
		var licount = "";
		var pgcount = 0;  
    jQuery('.firstpage').attr("href", bas_url+"/"+lang+"/drugs-list?"+attrs+"&pg=1");
		jQuery('.lastpage').attr("href", bas_url+"/"+lang+"/drugs-list?"+attrs+"&pg="+data.pageCount);
		jQuery('#pagerange').html(data.firstRowOnPage +'-'+ data.lastRowOnPage);
		jQuery('#pagetotal').html(data.pageCount);
		
			for(countit=1; countit <= (data.pageSize-1); countit ++)
		{
			if((data.lastRowOnPage - countit) > 0)
			{
				if (getUrlParameter("pg") === undefined) {
					pgcount = 0;
				}
				else{
				pgcount = getUrlParameter("pg");
				}
        if((parseInt(pgcount)+parseInt(countit)) > data.pageCount){
        break;         
         }
				licount += '<li id="'+(parseInt(pgcount)+parseInt(countit))+'" class="pager__item"><a href="'+bas_url+"/"+lang+"/drugs-list?"+attrs+"&pg="+(parseInt(pgcount)+parseInt(countit))+'">'+(parseInt(pgcount)+parseInt(countit))+'</a></li>';
			
      }
		}
      
    if(pgcount ==data.pageCount){
      licount += '<li class="pager__item pager__item--last">'+((lang=="en")? "End":"النهاية")+'</li>';
   }  
		jQuery('#pgnumber').html(licount);
      
			if (data.pageCount <= 0) {
				jQuery('.paginations').hide();
			} else if (data.currentPage < data.pageCount) { jQuery('.paginations').show();
				jQuery('.nextbutton').attr("data-maxpage", data.pageCount);
			} else if (data.currentPage == data.pageCount) { jQuery('.paginations').show();
				jQuery('.prevbutton').attr("data-minpage", data.pageCount);
			}

        if(data.currentPage >1){
       jQuery('.prevbutton').show();
        jQuery('.prevbutton').attr("href",bas_url+(window.location.pathname)+"?"+attrs+"&pg="+(data.currentPage-1));
         }else{
            jQuery('.prevbutton').hide();
         }
      if(data.currentPage < data.pageCount && (data.pageCount >1)){
         jQuery('.nextbutton').show();
        jQuery('.nextbutton').attr("href",bas_url+(window.location.pathname)+"?"+attrs+"&pg="+(data.currentPage+1))
         }else{
            jQuery('.nextbutton').hide();
         } 
			for (count in results) {
				drugs_list_table += '<tr><td><span class="en-text">' + results[count].scientificName + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].tradeName + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].strength + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].doesageForm + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].price + '</span></td>';
				drugs_list_table += ' <td><a href="#"  id="drugsdetails" data-toggle="modal" data-target=".item-modal" data-scientificName="' + results[count].scientificName + '" data-storageConditions="' + results[count].storageConditions + '"data-tradeName="' + results[count].tradeName + '" data-strength="' + results[count].strength + '" data-strengthUnit="' + results[count].strengthUnit + '" data-size="' + results[count].size + '" data-sizeUnit="' + results[count].sizeUnit + '" data-shelfLife="' + results[count].shelfLife + '" data-registerYear="' + results[count].registerYear + '" data-registerNumber="' + results[count].registerNumber + '" data-productControl="' + results[count].productControl + '" data-price="' + results[count].price + '" data-packageType="' + results[count].packageType + '" data-packageSize="' + results[count].packageSize + '" data-marketingStatus="' + results[count].marketingStatus + '" data-marketingCompany="' + results[count].marketingCompany + '" data-manufacturerName="' + results[count].manufacturerName + '" data-companyName="' + results[count].companyName + '" data-manufacturerCountry="' + results[count].manufacturerCountry + '" data-legalStatus="' + results[count].legalStatus + '" data-imageUrl="' + results[count].imageUrl + '" data-drugType="' + results[count].drugType + '" data-doesageForm="' + results[count].doesageForm + '" data-authorizationStatus="' + results[count].authorizationStatus + '" data-atcCode1="' + results[count].atcCode1 + '" data-atcCode2="' + results[count].atcCode2 + '" data-descriptionCode="' + results[count].descriptionCode + '" data-administrationRoute="' + results[count].administrationRoute +'" data-distributionArea="' + results[count].distributionArea +'" data-companyCountryEn="' + results[count].companyCountryEn +'" data-additionalManufacturerCountry="' + results[count].additionalManufacturerCountry + '" data-additionalManufacturer="' + results[count].additionalManufacturer + '">' + (lang == "en" ? "Details" : "التفاصيل") + '</a></td>';
				drugs_list_table += '</tr>';
			}
			drugs_list_table += '</tbody>';
			jQuery('#drugslisttable').html(drugs_list_table);
    }
		});
    jQuery('#drugs_loading').hide();
  }else{
	
		jQuery.getJSON(drugs_json, function(data) {
			var countit = 1;
			var licount = jQuery('#pgnumber').html();
			var pgcount = 0;
			
			jQuery('.firstpage').attr("href", bas_url+"/"+lang+"/drugs-list?pg=1");
			jQuery('.lastpage').attr("href", bas_url+"/"+lang+"/drugs-list?pg="+data.pageCount);
			jQuery('#pagerange').html(data.firstRowOnPage +'-'+ data.lastRowOnPage);
			jQuery('#pagetotal').html(data.pageCount);
			
		if (getUrlParameter("pg") === undefined){
			data.currentPage = 0;
			licount += '<li class="pager__item is-active" style="display:none;" ><a href="">'+(data.currentPage+1)+'</a></li>';
		}else{
			licount += '<li class="pager__item is-active"><a href="">'+data.currentPage+'</a></li>';
		}
			for(countit=1; countit <= (data.pageSize-1); countit ++)
			{
				if((data.lastRowOnPage - countit) > 0)
				{
					if (getUrlParameter("pg") === undefined) {
						pgcount = 0;
					}
					else{
					pgcount = getUrlParameter("pg");
					}
         if((parseInt(pgcount)+parseInt(countit)) > data.pageCount){
        break;         
         }
					licount += '<li id="'+(parseInt(pgcount)+parseInt(countit))+'" class="pager__item"><a href="'+bas_url+"/"+lang+"/drugs-list?pg="+(parseInt(pgcount)+parseInt(countit))+'">'+(parseInt(pgcount)+parseInt(countit))+'</a></li>';
						
				}
			}
      
      if(pgcount == data.pageCount){
      licount += '<li class="pager__item pager__item--last" >'+((lang=="en")? "End":"النهاية")+'</li>';
   } 
		
			jQuery('#pgnumber').html(licount);

		
			results = data.results;
			
			

			if (data.pageCount <= 0) {
				jQuery('.paginations').hide();
			} else if (data.currentPage < data.pageCount) { jQuery('.paginations').show();
				jQuery('.nextbutton').attr("data-maxpage", data.pageCount);
			} else if (data.currentPage == data.pageCount) { jQuery('.paginations').show();
				jQuery('.prevbutton').attr("data-minpage", data.pageCount);
			}
      
      if(data.currentPage >1){
       jQuery('.prevbutton').show();
        jQuery('.prevbutton').attr("href",bas_url+(window.location.pathname)+"?pg="+(data.currentPage-1));
         }else{
            jQuery('.prevbutton').hide();
         }
      if(data.currentPage < data.pageCount && (data.pageCount >1)){
         jQuery('.nextbutton').show();
        jQuery('.nextbutton').attr("href",bas_url+(window.location.pathname)+"?pg="+(data.currentPage+1))
         }else{
            jQuery('.nextbutton').hide();
         }

			for (count in results) {
				drugs_list_table += '<tr><td><span class="en-text">' + results[count].scientificName + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].tradeName + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].strength + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].doesageForm + '</span></td>';
				drugs_list_table += '<td><span class="en-text">' + results[count].price + '</span></td>';
				drugs_list_table += ' <td><a href="#"  id="drugsdetails" data-toggle="modal" data-target=".item-modal" data-scientificName="' + results[count].scientificName + '" data-storageConditions="' + results[count].storageConditions + '"data-tradeName="' + results[count].tradeName + '" data-strength="' + results[count].strength + '" data-strengthUnit="' + results[count].strengthUnit + '" data-size="' + results[count].size + '" data-sizeUnit="' + results[count].sizeUnit + '" data-shelfLife="' + results[count].shelfLife + '" data-registerYear="' + results[count].registerYear + '" data-registerNumber="' + results[count].registerNumber + '" data-productControl="' + results[count].productControl + '" data-price="' + results[count].price + '" data-packageType="' + results[count].packageType + '" data-packageSize="' + results[count].packageSize + '" data-marketingStatus="' + results[count].marketingStatus + '" data-marketingCompany="' + results[count].marketingCompany + '" data-manufacturerName="' + results[count].manufacturerName + '" data-companyName="' + results[count].companyName +'" data-manufacturerCountry="' + results[count].manufacturerCountry + '" data-legalStatus="' + results[count].legalStatus + '" data-imageUrl="' + results[count].imageUrl + '" data-drugType="' + results[count].drugType + '" data-doesageForm="' + results[count].doesageForm + '" data-authorizationStatus="' + results[count].authorizationStatus + '" data-atcCode1="' + results[count].atcCode1 + '" data-atcCode2="' + results[count].atcCode2 + '" data-descriptionCode="' + results[count].descriptionCode +  '" data-administrationRoute="' + results[count].administrationRoute +'" data-distributionArea="' + results[count].distributionArea +'" data-companyCountryEn="' + results[count].companyCountryEn +'" data-additionalManufacturerCountry="' + results[count].additionalManufacturerCountry + '" data-additionalManufacturer="' + results[count].additionalManufacturer + '">' + (lang == "en" ? "Details" : "التفاصيل") + '</a></td>';
				drugs_list_table += '</tr>';
			}
			drugs_list_table += '</tbody>';
			jQuery('#drugslisttable').html(drugs_list_table);
			jQuery('#drugs_loading').hide();

		});
    jQuery('#drugs_loading').hide();
  }
	
	

});


jQuery(document).on('click', '#submit', function(e) {

	var TradeName = jQuery('#TradeName').val();
  var ScientificName = jQuery('#ScientificName').val();
  var Agent = jQuery('#Agent').val();
  var ManufacturerName = jQuery('#ManufacturerName').val();
  var RegNo = jQuery('#RegNo').val();
  
	var search_table = "";
	drugs_json_search = searchjson;
  var attrs="TradeName="+TradeName+"&ScientificName="+ScientificName+"&Agent="+Agent+"&ManufacturerName="+ManufacturerName+"&RegNo="+RegNo;
  drugs_json_search +=attrs;
   
	drugs_json_search +="&page=1";
  if(TradeName =="" && ScientificName=="" && Agent=="" && ManufacturerName=="" && RegNo==""){
    history.pushState(null, null, bas_url+(window.location.pathname));
    location.reload();
  }
  var count = "";
	var results = "";
		jQuery('#pgnumber').html("");
// 	console.log(drugs_json_search);
	
	jQuery('#drugslisttable').html('');
	jQuery('.paginations').hide();

	e.preventDefault();
  if(getUrlParameter("pg") !== undefined){
  history.pushState(null, null, bas_url+(window.location.pathname)+"?"+attrs+"&pg=1");
}
	search_table += '<thead><tr>';
	search_table += '<th>' + (lang == "en" ? "Scientific Name" : "الاسم العلمي") + '</th>';
	search_table += '<th>' + (lang == "en" ? "Trade Name" : "الاسم التجاري") + '</th>';
	search_table += '<th>' + (lang == "en" ? "Strength" : "التركيز") + '</th>';
	search_table += '<th>' + (lang == "en" ? "Doesage Form" : "الشكل الصيدلاني") + '</th>';
	search_table += '<th>' + (lang == "en" ? "Price" : "السعر") + '</th>';
	search_table += '<th>' + (lang == "en" ? "Details" : "التفاصيل") + '</th>';
	search_table += '</tr></thead>';
	search_table += '<tbody>';
  
  jQuery.getJSON(drugs_json_search, function(data) {
      var countit = 1;
			var licount = "";
			var pgcount = 0; 
			results = data.results;
    if( results == null || data == null || jQuery.isEmptyObject(results)){
			search_table += '<tr><td colspan="6"><h3 class="no-result">' + (lang == "en" ? "No Results Found" : " لا توجد نتائج ") + '</h3></td></tr>';
			search_table += '</tbody>';
			jQuery('#drugslisttable').html(search_table);
		}
		else{

			if (data.pageCount <= 0) {
				jQuery('.paginations').hide();
			} else if (data.currentPage < data.pageCount) { jQuery('.paginations').show();
				jQuery('.nextbutton').attr("data-maxpage", data.pageCount);
			} else if (data.currentPage == data.pageCount) { jQuery('.paginations').show();
				jQuery('.prevbutton').attr("data-minpage", data.pageCount);
			}

        if(data.currentPage >1){
       jQuery('.prevbutton').show();
        jQuery('.prevbutton').attr("href",bas_url+(window.location.pathname)+"?"+attrs+"&pg="+(data.currentPage-1));
         }else{
            jQuery('.prevbutton').hide();
         }
      if(data.currentPage < data.pageCount && (data.pageCount >1)){
         jQuery('.nextbutton').show();
        jQuery('.nextbutton').attr("href",bas_url+(window.location.pathname)+"?"+attrs+"&pg="+(data.currentPage+1))
         }else{
            jQuery('.nextbutton').hide();
         }
      
      jQuery('.firstpage').attr("href", bas_url+"/"+lang+"/drugs-list?pg=1");
			jQuery('.lastpage').attr("href", bas_url+"/"+lang+"/drugs-list?pg="+data.pageCount);
			jQuery('#pagerange').html(data.firstRowOnPage +'-'+ data.lastRowOnPage);
			jQuery('#pagetotal').html(data.pageCount);
			
	if (getUrlParameter("pg") === undefined){
			data.currentPage = 0;
			licount += '<li class="pager__item is-active" style="display:none;" ><a href="">'+(data.currentPage+1)+'</a></li>';
		}else{
			licount += '<li class="pager__item is-active"><a href="">'+data.currentPage+'</a></li>';
		}
      
      for(countit=1; countit <= (data.pageSize-1); countit ++)
		{
			if((data.lastRowOnPage - countit) > 0)
			{
				if (getUrlParameter("pg") === undefined) {
					pgcount = 0;
				}
				else{
				pgcount = getUrlParameter("pg");
				}
        if((parseInt(pgcount)+parseInt(countit)) > data.pageCount){
        break;         
         }
				licount += '<li id="'+(parseInt(pgcount)+parseInt(countit))+'" class="pager__item" ><a href="'+bas_url+"/"+lang+"/drugs-list?"+attrs+"&pg="+(parseInt(pgcount)+parseInt(countit))+'">'+(parseInt(pgcount)+parseInt(countit))+'</a></li>';
			
      }
		}
      
    if(pgcount ==data.pageCount){
      licount += '<li  class="pager__item pager__item--last">'+((lang=="en")? "End":"النهاية")+'</li>';
   }  
		jQuery('#pgnumber').html(licount);
      
			for (count in results) {
				search_table += '<tr><td><span class="en-text">' + results[count].scientificName + '</span></td>';
				search_table += '<td><span class="en-text">' + results[count].tradeName + '</span></td>';
				search_table += '<td><span class="en-text">' + results[count].strength + '</span></td>';
				search_table += '<td><span class="en-text">' + results[count].doesageForm + '</span></td>';
				search_table += '<td><span class="en-text">' + results[count].price + '</span></td>';
				search_table += ' <td><a href="#"  id="drugsdetails" data-toggle="modal" data-target=".item-modal" data-scientificName="' + results[count].scientificName + '" data-storageConditions="' + results[count].storageConditions + '" data-tradeName="' + results[count].tradeName + '" data-strength="' + results[count].strength + '" data-strengthUnit="' + results[count].strengthUnit + '" data-size="' + results[count].size + '" data-sizeUnit="' + results[count].sizeUnit + '" data-shelfLife="' + results[count].shelfLife + '" data-registerYear="' + results[count].registerYear + '" data-registerNumber="' + results[count].registerNumber + '" data-productControl="' + results[count].productControl + '" data-price="' + results[count].price + '" data-packageType="' + results[count].packageType + '" data-packageSize="' + results[count].packageSize + '" data-marketingStatus="' + results[count].marketingStatus + '" data-manufacturerName="' + results[count].manufacturerName + '" data-companyName="' + results[count].companyName+ '" data-manufacturerCountry="' + results[count].manufacturerCountry + '" data-legalStatus="' + results[count].legalStatus + '" data-imageUrl="' + results[count].imageUrl + '" data-drugType="' + results[count].drugType + '" data-doesageForm="' + results[count].doesageForm + '" data-authorizationStatus="' + results[count].authorizationStatus + '" data-atcCode1="' + results[count].atcCode1 + '" data-atcCode2="' + results[count].atcCode2 + '" data-descriptionCode="' + results[count].descriptionCode +'" data-administrationRoute="' + results[count].administrationRoute +'" data-distributionArea="' + results[count].distributionArea +'" data-companyCountryEn="' + results[count].companyCountryEn + '" data-additionalManufacturerCountry="' + results[count].additionalManufacturerCountry + '" data-marketingCompany="' + results[count].marketingCompany + '" data-additionalManufacturer="' + results[count].additionalManufacturer + '">' + (lang == "en" ? "Details" : "التفاصيل") + '</a></td>';
				search_table += '</tr>';
			}
			search_table += '</tbody>';
			jQuery('#drugslisttable').html(search_table);
    }
		});

});

function myfunction(x){
	
	if(x==1){	
		document.getElementById("click1").style.background="#163977";
		document.getElementById("click1").style.color="#ffffff";
		document.getElementById("change1").style.display="none";
		document.getElementById("replace1").style.display="inline";
	}else{	
		document.getElementById("click2").style.background="#163977";
		document.getElementById("click2").style.color="#ffffff";
		document.getElementById("change2").style.display="none";
		document.getElementById("replace2").style.display="inline";
	}
	
}

jQuery(document).on('click', '#drugsdetails', function(e) {
	
	
	console.log(jQuery(this).data().registernumber);
	drugs_json_registernumber = registernumberjson;
	var search = "search="+jQuery(this).data().registernumber;
	drugs_json_registernumber += search
	jQuery.getJSON(drugs_json_registernumber, function(dataj) {
		var result = dataj.results;
		console.log(result);
		var countregisternumber = 0;
		var nullregisternumber = 0;
		var registernumberid = '';
		var countnum = 3;
		for(var num=0;num<result.length;num++){
			countregisternumber++;
			registernumberid = "#agentname"+countregisternumber;
			jQuery(registernumberid).html((result[num].nameEn == null ? (lang == "en" ? "No value" : "لا يوجد") : result[num].nameEn));
		}
		if(countregisternumber<3){
			nullregisternumber = 3-countregisternumber;
			for(var num=0;num<nullregisternumber;num++){
			registernumberid = "#agentname"+countnum;
			jQuery(registernumberid).html((lang == "en" ? "No value" : "لا يوجد"));
			countnum--;
			}
		}
	
	
	});
	
	
	var reportFile= bas_url + "/system/files/2021/" + jQuery(this).data().registernumber + ".pdf";


	function doesFileExist(urlToFile) {
		var xhr = new XMLHttpRequest();
		xhr.open('HEAD', urlToFile, false);
		xhr.send();
		 
		if (xhr.status == "404") {
			return false;
		} else {
			return true;
		}
	}
		
	var resultFile = doesFileExist(reportFile); 

    jQuery('#drugReports').html(( resultFile == false ? (lang == "en" ? "No value" : "لا يوجد") : "<p><a href=" + reportFile + " target='_blank'><img src='/themes/custom/sfda/assets/images/icons/pdf.svg' class='img-fluid svg-3' style='width: 47px;'></a></p>" ));

	jQuery('#scientificName').html((jQuery(this).data().scientificname == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().scientificname));
	//jQuery('#scientificNamee').html((jQuery(this).data().scientificname == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().scientificname));
	jQuery('#storageConditions').html((jQuery(this).data().storageconditions == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().storageconditions));
	jQuery('#tradeName').html((jQuery(this).data().tradename == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().tradename));
	jQuery('#tradeNamee').html((jQuery(this).data().tradename == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().tradename));
	//jQuery('#strength').html((jQuery(this).data().strength == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().strength));
	jQuery('#strengthUnit').html((jQuery(this).data().strengthunit == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().strengthunit));
	jQuery('#size').html((jQuery(this).data().size == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().size));
	jQuery('#sizeUnit').html((jQuery(this).data().sizeunit == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().sizeunit));
	jQuery('#shelfLife').html((jQuery(this).data().shelflife == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().shelflife));
	//jQuery('#registerYear').html((jQuery(this).data().registeryear == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().registeryear));
	jQuery('#registerNumber').html((jQuery(this).data().registernumber == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().registernumber));
	jQuery('#productControl').html((jQuery(this).data().productcontrol == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().productcontrol));
	jQuery('#price').html((jQuery(this).data().price == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().price));
	jQuery('#packageType').html((jQuery(this).data().packagetype == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().packagetype));
	jQuery('#packageSize').html((jQuery(this).data().packagesize == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().packagesize));
	jQuery('#marketingStatus').html((jQuery(this).data().marketingstatus == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().marketingstatus));
	jQuery('#companyName').html((jQuery(this).data().companyname == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().companyname));
	jQuery('#manufacturerName').html((jQuery(this).data().manufacturername == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().manufacturername));
	jQuery('#manufacturerCountry').html((jQuery(this).data().manufacturercountry == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().manufacturercountry));
	jQuery('#legalStatus').html((jQuery(this).data().legalstatus == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().legalstatus));
	jQuery('#imageUrl').html((jQuery(this).data().imageurl == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().imageurl));
	//jQuery('#drugType').html((jQuery(this).data().drugtype == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().drugtype));
	jQuery('#doesageForm').html((jQuery(this).data().doesageform == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().doesageform));
	//jQuery('#doesageForm').html((jQuery(this).data().doesageform == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().doesageform));
	//jQuery('#doesageForm').html((jQuery(this).data().doesageform == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().doesageform));
	//jQuery('#doesageFormm').html((jQuery(this).data().doesageform == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().doesageform));
	jQuery('#authorizationStatus').html((jQuery(this).data().authorizationstatus == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().authorizationstatus));
	jQuery('#atcCode1').html((jQuery(this).data().atccode1 == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().atccode1));
	jQuery('#atcCode2').html((jQuery(this).data().atccode2 == null || jQuery(this).data().atccode2 == "" ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().atccode2));
	jQuery('#descriptionCode').html((jQuery(this).data().descriptioncode == null || jQuery(this).data().descriptioncode == "" ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().descriptioncode));
	jQuery('#additionalManufacturerCountry').html((jQuery(this).data().additionalmanufacturercountry == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().additionalmanufacturercountry));
	jQuery('#additionalManufacturer').html((jQuery(this).data().additionalmanufacturer == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().additionalmanufacturer));
	//
	jQuery('#strength').html((jQuery(this).data().strength == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().strength));
	jQuery('#administrationRoute').html((jQuery(this).data().administrationroute == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().administrationroute));
	jQuery('#distributionArea').html((jQuery(this).data().distributionarea == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().distributionarea));
	//jQuery('#companyCountryAr').html((jQuery(this).data().companycountryar == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().companycountryar));
	jQuery('#companyCountryEn').html((jQuery(this).data().companycountryen == null ? (lang == "en" ? "No value" : "لا يوجد") : jQuery(this).data().companycountryen));

});

