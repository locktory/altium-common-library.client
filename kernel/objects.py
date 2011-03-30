#-*- coding: utf-8 -*-

import datetime
import xml.etree.ElementTree as xmltree

lxml_installed = False

try:
	from lxml import etree as xmltree
	lxml_installed = True
	print("running with lxml.etree")
except ImportError:
	try:
		# Python 2.5
		import xml.etree.cElementTree as xmltree
		print("running with cElementTree on Python 2.5+")
	except ImportError:
		try:
			# Python 2.5
			import xml.etree.ElementTree as xmltree
			print("running with ElementTree on Python 2.5+")
		except ImportError:
			try:
				# normal cElementTree install
				import cElementTree as xmltree
				print("running with cElementTree")
			except ImportError:
				try:
					# normal ElementTree install
					import elementtree.ElementTree as xmltree
					print("running with ElementTree")
				except ImportError:
					print("Failed to import ElementTree from any known place")

print


#######################

class RequestMessage():
	Name = 'XML Query'

	def __init__(self, method, mode='request'):

		self.type = mode
		self.method = method
		self.values = {}
		self.data = []
		self.id = 0



	def add_value(self, name, value):
		self.values[name] = value


	def add_item(self, item):
		self.data.append(item)


	def build(self):

		return



class ResponseMessage():
	Name = 'XML Query'

	def __init__(self, xmldata=None):

		self.type = None
		self.xmldata = xmldata
		self.error = None
		self.data = []
		self.method = None
		self.values = {}
		self.id = 0



	def parse(self):
		if not self.xmldata:
			print 'no data'
			self.error = 'no data to parse'
			return

		try:
			xmldata = eltree.XML(self.xmldata)


		except eltree.ParseError, e:
			print 'parse error %s' % (e,)
			self.error = e
			return

		print xmldata.tag
		print xmldata.get('type')

		self.type = xmldata.get('type')

		if not xmldata.tag == 'query':
			print 'Warning: WFT?'

		method = xmldata.find('method')

		### только текстовые !!
		for value in method.findall('value'):
			self.values[value.get('name')] = value.get('value')

		print 'VALUES', self.values

		data = xmldata.find('data')

		elements = data.findall('component')

		for element in elements:
			
			manufacturer = element.get('manufacturer')
			partnumber = element.get('partnumber')

			if not isinstance(manufacturer, unicode):
				manufacturer = unicode(manufacturer, 'utf-8')

			if not isinstance(partnumber, unicode):
				partnumber = unicode(partnumber, 'utf-8')

			el = Component(manufacturer, partnumber)

			for parameter in element.findall('parameter'):
				name = parameter.get('name')
				value = parameter.get('value')
				mode = parameter.get('type')

				print '\t', name, value, mode

				el.set(name, value, mode)

			self.data.append(el)



		def _element2dict(element):

			if len(element):
				for child in element:
					_element2dict(child)

		return self

class QueryItem():

	def __init__(self, element):
		self.element = element

	def build(self, builder):
		return


class Component():

	def __init__(self, manufacturer='Unknown', partnumber='Unknown'):
		self._manufacturer = manufacturer
		self._partnumber = partnumber
		self._parameters = {}

	def manufacturer(self):
		""" возвращает производителя компонента """
		return self._manufacturer

	def partnumber(self):
		""" возвращает артикул компонента """
		return self._partnumber

	def __iter__(self):
		return iter(self._parameters.values())

	def get(self, parameter):
		""" возвращает параметр с наименованием parameter """
		return self._parameters.get(parameter)

	def set(self, parameter):
		""" добавляет новый параметр """
		if not isinstance(parameter, Parameter):
			raise TypeError, "Parameter object expected"

		self._parameters[parameter.name] = parameter

	def build(self):
		""" возвращает Element компонента """
		el = xmltree.Element('component')

		el.set('manufacturer', self.manufacturer())
		el.set('partnumber', self.partnumber())

		for parameter in self:
			el.append(parameter.build())

		return el

	def xml(self):
		""" возвращает pretty_printed XML компонента НЕ НУЖЕН ТУТ """
		xmlobject = self.build()

		if lxml_installed:
			xml = xmltree.tostring(xmlobject, encoding='utf-8', xml_declaration=True, pretty_print=True)

		else:
			from xml.dom import minidom

			barexml = xmltree.tostring(xmlobject, encoding='utf-8')
			xml = minidom.parseString(barexml).toprettyxml(indent='\t', encoding='utf-8')

		return xml

	def parse(self, xml):
		""" генерирует компонент из XML """
		try:
			el = xmltree.XML(xml)

		except:
			print 'Non-valid XML: error parsing document'
			return

		if not el.tag == 'component':
			raise Exception, 'Non-valid XML: it is not a component'

		self._manufacturer = el.get('manufacturer')
		self._partnumber = el.get('partnumber')

		for sub in el.findall('parameter'):
			try:
				parameter = Parameter(sub.get('name'), sub.get('value'), sub.get('type'))
				self.set(parameter)
			except:
				print 'Non-valid XML: it is not parameter'


class Parameter():

	def __init__(self, name, value, mode):
		if not name:
			raise Exception, 'Empty Parameter Name'

		self._name = name
		self._value = value
		self._type = mode

	def name(self):
		""" возвращает наименование параметра """
		return self._name

	def value(self):
		""" возвращает строковое значение параметра """
		return self._value

	def type(self):
		"""возвращает тип параметра """
		return self._type

	def real(self):
		""" возвращает приведенное значение параметра НЕПРОВЕРЕНО """
		if self._type == 'string':
			return unicode(self._value)

		elif self._type == 'float':
			return float(self._value)

		elif self._type == 'datetime':
			return datetime.datetime(self._value)

	def build(self):
		""" возвращает Element параметра """
		el = xmltree.Element('parameter')
		el.set('name', self.name())
		el.set('value', self.value())
		el.set('type', self.type())

		return el

if __name__ == '__main__':

	with open('../debug/pretty.xml', 'r') as f:
		xml = f.read()

	q = Component()
	q.parse(xml)

	print
	print q.xml()