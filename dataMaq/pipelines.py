from itemadapter import ItemAdapter
import csv
import os
import json

class DatamaqPipeline:
	def process_item(self, item, spider):
		self.setInfoInCSV(ItemAdapter(item))
		return item

	def send_log_system(self, type_message, message):
		print (f'[ {type_message} ] {message}')

	def setInfoInCSV(self, dictData):
		titles, data = self.convertDictInCSV(dictData)
		self.send_log_system('DEBUG', 'Empresa Coletada - {}'.format(dictData['Empresa']))

		if 'empresas.csv' in os.listdir('./outputs/'):
			file_csv = open('./outputs/empresas.csv', 'a+', encoding='utf-8')
			file_csv.write(data)
		else:
			file_csv = open('./outputs/empresas.csv', 'a+', encoding='utf-8')
			file_csv.write(titles + data)

		file_csv.close()

	def convertDictInCSV(self, dictData):
		array_titles = ['Setor', 'Empresa', 'Endereço', 'CEP', 'CNPJ', 'Cidade', 'Estado', 'Contato', 'Telefone', 'EMail', 'Site',
		'Pasta', 'NAssociação', 'DatadeFundação', 'DatadeAssociação', 'DatadeReintegração', 'DatadeDesligamento', 'TipodeCNPJ', 'AfiliadoaoSindimaq',
		'UrlEmpresa', 'Produtos']
		array_data = []

		for key in array_titles:
			if key in dictData.keys():
				if str(key) == 'Produtos':
					if dictData[key] != []:
						array_data.append(str(dictData[key]).replace(';', '').replace('[', '').replace(']', '').replace("'", "").strip())
					else:
						array_data.append('')
				else:
					if dictData[key] is not None:
						array_data.append(str(dictData[key]).replace(';', ','))
					else:
						array_data.append('')
			else:
				array_data.append('')

		string_title = str(';'.join(array_titles)) + '\n'
		string_data = str(';'.join(array_data)) + '\n'

		return string_title, string_data