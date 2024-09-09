from lxml import etree as ET
read_params = [
    {'com': 3,'slave': 1, 'count': 9},
    {'com': 3,'slave': 2, 'count': 9},
    {'com': 3,'slave': 3, 'count': 9},
    {'com': 3,'slave': 4, 'count': 9},
    {'com': 3,'slave': 5, 'count': 9},
    {'com': 3,'slave': 6, 'count': 9},
    {'com': 3,'slave': 7, 'count': 9},
    {'com': 3,'slave': 8, 'count': 9},
    {'com': 3,'slave': 9, 'count': 9},
    {'com': 3,'slave': 10, 'count': 9},
    {'com': 3,'slave': 11, 'count': 9},
    {'com': 3,'slave': 12, 'count': 9},
    {'com': 3,'slave': 13, 'count': 9},
    {'com': 3,'slave': 14, 'count': 9},
    {'com': 3,'slave': 15, 'count': 9},
    {'com': 3,'slave': 16, 'count': 9},
    {'com': 3,'slave': 17, 'count': 9},
    {'com': 3,'slave': 18, 'count': 9},
    {'com': 3,'slave': 19, 'count': 9},
    {'com': 3,'slave': 20, 'count': 9}
]
def generate_Modbus_xml(xml_file):
    root = ET.Element("systemvariables", {"version": "4"})
    namespace1 = ET.SubElement(root, "namespace", {"name": "", "comment": "", "interface": ""})
    namespace2 = ET.SubElement(namespace1, "namespace", {"name": "ModbusRegister", "comment": "", "interface": ""})
    for read_param in read_params:
        Slave_namespace = ET.SubElement(namespace2, "namespace",
                                          {"name": 'Slave' + "_" + str(read_param['slave']), "comment": "",
                                           "interface": ""})
        for i in range(read_param['count']):
            Register_namespace =ET.SubElement(Slave_namespace, "variable",
                                          {"anlyzLocal": "2",
                                           "readOnly": "false",
                                           "valueSequence": "false",
                                           "unit": "",
                                           "name": 'Register' + '_'+str(i),
                                           "comment": "",
                                           "bitcount": "32",
                                           "isSigned": "false",
                                           "encoding": "65001",
                                           "type": "int"})
    # 格式化 XML 输出
    tree = ET.ElementTree(root)
    pretty_xml = '<?xml version="1.0" ?>\n' + ET.tostring(tree, pretty_print=True, encoding='unicode')

    # 写入文件
    with open(xml_file, "w") as f:
        f.write(pretty_xml)


def generate_Modbus_FDX_Description(xml_file):
    root = ET.Element("canoefdxdescription", {"version": "1.0"})
    for read_param in read_params:
        datagroup = ET.SubElement(root, "datagroup", {"groupID": str(read_param['slave']), "size": str(read_param['slave']*2)})
        ET.SubElement(datagroup, "identifier").text = 'slave'+'_'+str(read_param['slave'])

        for i in range(read_param['count']):
            item = ET.SubElement(datagroup, "item", {"offset": str(i*2), "size": '2', "type": "uint16"})
            ET.SubElement(item, "sysvar", {"name": 'Register' + '_'+str(i),
                                           "namespace": "ModbusRegister::" + 'Slave' + "_" + str(read_param['slave']),
                                           "value": "raw"})
        # 格式化 XML 输出
        tree = ET.ElementTree(root)
        pretty_xml = '<?xml version="1.0" ?>\n' + ET.tostring(tree, pretty_print=True, encoding='unicode')

        # 写入文件
        with open(xml_file, "w") as f:
            f.write(pretty_xml)


def generate_dbc_FDX( xml_file):
    root = ET.Element("canoefdxdescription", {"version": "1.0"})

    for read_param in read_params:
        dategroup = ET.SubElement(root, "datagroup", {"groupID": str(read_param['slave']), "size": ""})
        ET.SubElement(dategroup, "identifier").text = 'slave' + ' ' + str(read_param['slave'])


        for i in range(read_param['count']):
            item = ET.SubElement(dategroup, "item", {"offset": str(i*2), "size": "2", "type": "uint16"})
            ET.SubElement(item, "sysvar", {"name": 'Register' + '_'+str(i),
                                         "namespace": "ModbusRegister::" + 'Slave' + "_" + str(read_param['slave']),
                                         "value": "raw"})

        dategroup.set("size", str(read_param['count']*2))

    # 格式化 XML 输出
    tree = ET.ElementTree(root)
    pretty_xml = '<?xml version="1.0" ?>\n' + ET.tostring(tree, pretty_print=True, encoding='unicode')

    # 写入文件
    with open(xml_file, "w") as f:
        f.write(pretty_xml)


if __name__ == "__main__":
    generate_Modbus_xml("modbus_sys.xml")
    generate_dbc_FDX('modbus_FDX_Description.xml')