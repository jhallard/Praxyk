// JavaScript Document
function footer_init(){
footer = '<div class="divPanel">\
<div class="row-fluid">\
<div class="span3" id="footerArea1">\
<h3>About Company</h3>\
<p>Our goal is to implement the most popular machine-learning tools and offer access to their predictive capabilities as a service through a dedicated API. This makes the predictive power of machine-learning more accessible, especially for small businesses.</p>\
<p> \
<a href="terms_of_service.html" title="Terms of Service">Terms of Service</a><br />\
<a href="privacy_policy.html" title="Privacy Policy">Privacy Policy</a><br />\
<a href="#" title="FAQ">FAQ</a><br />\
<a href="#" title="Sitemap">Sitemap</a><br />\
<a href="http://www.github.com/jhallard/praxyk" title="Github">Github</a>\
</p>\
</div>\
<div class="span3" id="footerArea2"></div>\
<div class="span3" id="footerArea3"></div>\
<div class="span3" id="footerArea4">\
<h3>Get in Touch</h3>\
<ul id="contact-info">\
<li>\
<i class="general foundicon-phone icon"></i>\
<span class="field">Phone:</span>\
<br />\
(123) 456 7890\
</li>\
<li>\
<i class="general foundicon-mail icon"></i>\
<span class="field">Email:</span>\
<br />\
<a href="mailto:praxykservices@gmail.com" title="Email">support@praxyk.com</a>\
</li>\
<li>\
<i class="general foundicon-home icon" style="margin-bottom:50px"></i>\
<span class="field">Address:</span>\
<br />\
1156 High Street<br />\
Santa Cruz, Califoria 95064<br />\
</li>\
</ul>\
</div>\
</div>\
<div class="row-fluid">\
<div class="span12">\
<p class="copyright">Copyright &copy; 2015 Praxyk Group. All Rights Reserved.</p>\
</div>\
</div>\
</div>';

$("#divFooter").html(footer);
}
