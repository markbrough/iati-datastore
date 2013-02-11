import json
import re
import argparse
from datetime import datetime

def _fieldname(x):
    name = x['xml'].strip()
    valid = name.split('/')[-1]
    assert valid.startswith('@') or valid=='text()', 'XPath is neither an attribute nor a text() field: %s' % name
    assert not '_' in name
    name = name.replace('xml:lang','lang')
    name = name.replace('-','_')
    name = name.replace('/','__')
    name = name.replace('@','')
    name = name.replace('()','')
    assert re.match(r'^[A-Za-z0-9_]+$',name),name
    assert len(name), x
    return name

def _typename(x):
    return x.get('format','UnicodeText')

def _nav(x):
    path = x['xml'].strip().split('/')
    pathcode = ','.join( '\'%s\''%x for x in path[:-1] )
    typename = _typename(x)
    typeparser = ''
    if typename=='DateTime': typeparser = ', parser=_parse_datetime'
    if typename=='Integer': typeparser = ', parser=_parse_int'
    if typename=='Float': typeparser = ', parser=_parse_float'
    if typename=='Boolean': typeparser = ', parser=_parse_boolean'
    if path[-1]=='text()':
        return '_nav(logger, xml, [%s], text=True%s)' % ( pathcode, typeparser )
    elif path[-1].startswith('@'):
        attrib = path[-1][1:]
        return '_nav(logger, xml, [%s], attrib=\'%s\'%s)' % ( pathcode, attrib, typeparser )
    assert False,'I can\'t process this path: %s' % x['xml']

def _parser_fields(data):
    out = []
    for x in data:
        name = _fieldname(x)
        typename = _typename(x)
        nav = _nav(x)
        out.append('data[\'%s\'] = %s' % (name,nav))
    return out

def _model_fields(data):
    out = []
    for x in data:
        name = _fieldname(x)
        typename = _typename(x)
        xpath = x['xml']
        out.append('%s = Column(%s)\t# %s' % (name,typename,xpath))
    return out

def codegen():
    print '#######'
    print '### Autogenerated models for model.py created on %s' % datetime.now()
    print '#######'
    with open('spec/spec.json','r') as f:
        specs = json.load(f)
    class_to_table = {x['classname']:x['tablename'] for x in specs}
    # Augment the spec with backreferencing foreign keys
    for spec in specs:
        for child in spec.get('children',[]):
            for x in specs:
                if x['classname']==child['class']:
                    x['foreign_key'] = {'name':spec['tablename']+'.id'}
    for spec in specs:
        print ''
        print 'class %s(Base):' % spec['classname']
        print '    __tablename__ = \'%s\'' % spec['tablename']
        print '    id = Column(Integer, primary_key=True)'
        for x in spec.get('children',[]):
            tablename = class_to_table[x['class']]
            print '    %s = relationship("%s",cascade="all")' % (tablename,x['class'])
        if 'foreign_key' in spec:
            print '    parent_id = Column(%s, ForeignKey(\'%s\'), nullable=False)' % (spec['foreign_key'].get('format','Integer'), spec['foreign_key']['name'])
        for x in _model_fields(spec['fields']): print '    '+x
        print '    @classmethod'
        print '    def _parse_xml(cls,logger,xml):'
        print '        data = {}'
        for x in _parser_fields(spec['fields']): print '        '+x
        print '        out = %s(**data)' % spec['classname']
        for x in spec.get('children',[]):
            print '        for child_xml in xml.findall(\'%s\'):' % x['xpath']
            print '            out.%s.append( %s._parse_xml(logger,child_xml) )' % (class_to_table[x['class']],x['class'])
        print '        return out'

if __name__=='__main__':
    codegen()
