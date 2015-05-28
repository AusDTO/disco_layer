url = require('url')
parsedURL = {
	"protocol":"https",
	"host":"www.dto.gov.au",
	"port":80,
	"pathname":"/sites/g/files/net261/themes/site/dto_whitesite/fonts/TradeGothicLT.ttf?1416195844",
	"depth":4}
	
// 'http://user:pass@host.com:8080/p/a/t/h?query=string#hash'
	
urlstring = url.format(parsedURL);

console.log(urlstring);	