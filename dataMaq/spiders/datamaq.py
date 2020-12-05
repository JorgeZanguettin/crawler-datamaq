import scrapy
import requests
import urllib.parse
from ..items import DatamaqItem
from bs4 import BeautifulSoup

class DatamaqSpider(scrapy.Spider):
    name = 'datamaq'
    allowed_domains = []
    custom_settings = {
        'ITEM_PIPELINES': {
            'dataMaq.pipelines.DatamaqPipeline': 400
        }
    }
    
    obj_bs4 = BeautifulSoup(requests.get('http://www.datamaq.org.br/SearchResult/AdditionalFilter?parentId=undefined&sectorName=undefined&isSegment=undefined').content, 'html.parser')
    array_urls = []
    for obj_url in obj_bs4.select('input.btn.btn-outline-info'):
        if 'showChildSector' in str(obj_url['onclick']):       
            id_categoria = str(obj_url['onclick']).replace("showChildSector('", "").replace("');", "").replace("', '", ",").split(',')[0]
            categoria = str(obj_url['onclick']).replace("showChildSector('", "").replace("');", "").replace("', '", ",").split(',')[1]

            url_categoria = 'http://www.datamaq.org.br/SearchResult/AccountIndustrialSectorList?industrialSectorId={}&sectorName={}&isSegment=undefined'.format(
                id_categoria,
                urllib.parse.quote_plus(categoria)
            )

            array_urls.append(url_categoria)

    start_urls = array_urls

    def parse(self, response):
        for empresa_block in response.css("table.table.table-sm.table-hover tbody tr::attr(onclick)").extract():
            yield scrapy.Request(self.getUrlEmpresa(empresa_block), callback=self.getEmpresaDetails, dont_filter=True)

    def getEmpresaDetails(self, response):
        self.item_empresa = DatamaqItem()
        
        self.item_empresa['UrlEmpresa'] = response.url
        for block_prop in response.css("div.container div.row"):
            field_name = block_prop.css("div.col-2 span::text").extract_first()
            if field_name is not None:
                field_name = str(field_name).replace(':', '').replace('º', '').replace(' ', '').replace('-', '').strip()
                field_value = block_prop.css("div.col span::text").extract_first()

                if field_value is None:
                    field_value = block_prop.css("div.col a::text").extract_first()
                    if field_value is not None:
                        field_value = str(field_value).strip()
                else:
                    field_value = str(field_value).strip()

                self.item_empresa[field_name] = field_value

        yield scrapy.Request(self.getUrlProdutos(response.xpath('/html/body/div[3]/div/div[1]/input/@onclick').extract_first()), callback=self.getProdutosDetails, dont_filter=True)

    def getProdutosDetails(self, response):
        self.item_empresa['Produtos'] = response.css('table.table.table-sm.table-hover tbody tr td a::text').extract()

        yield self.item_empresa

    def getUrlProdutos(self, empresa_block):
        propriedades = str(empresa_block).replace('openLineOfProduction(', '').replace(');', '').replace("'", "").split(', ')

        return 'http://www.datamaq.org.br/SearchResult/LineOfProduction?sectorId={}&sectorName={}&entityId={}&entityIDName={}&isSector={}'.format(
            propriedades[0],
            urllib.parse.quote_plus(propriedades[1]),
            propriedades[2],
            urllib.parse.quote_plus(propriedades[3]),
            propriedades[4],
        )

    def getUrlEmpresa(self, empresa_block):
        propriedades_empresa = str(empresa_block).replace('openAccountDetail(', '').replace(');', '').replace("'", "").split(', ')
        return 'http://www.datamaq.org.br/SearchResult/ShowManufacturer?sectorId={}&sectorName={}&entityId={}&entityIDName={}&sourceType=2&industrialInstallationProductId=&isSector=1'.format(
            propriedades_empresa[0],
            urllib.parse.quote_plus(propriedades_empresa[1]),
            propriedades_empresa[2],
            urllib.parse.quote_plus(propriedades_empresa[3]),
        )
