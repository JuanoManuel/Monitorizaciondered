from pysnmp.hlapi import *

def ComandSNMP(comunidad,host,oid):
	errorIndication, errorStatus, errorIndex, varBinds = next(
			getCmd(SnmpEngine(),
				CommunityData(comunidad),
				UdpTransportTarget((host,161)),
				ContextData(),
				ObjectType(ObjectIdentity(oid))))
	if errorIndication:
		print(errorIndication)
	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
	else:
		for varBind in varBinds:
			varB = (' = '.join([x.prettyPrint() for x in varBind]))
			resultado = varB.split()[2]
		return resultado
	return "Error"

def TupleComandSNMP(comunidad,host,oid):
	errorIndication, errorStatus, errorIndex, varBinds = next(
			getCmd(SnmpEngine(),
				CommunityData(comunidad),
				UdpTransportTarget((host,161)),
				ContextData(),
				ObjectType(ObjectIdentity(oid))))
	if errorIndication:
		print(errorIndication)
	elif errorStatus:
		print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex)-1][0] or '?'))
	else:
		for varBind in varBinds:
			varB = (' = '.join([x.prettyPrint() for x in varBind]))
			varB = varB.split('=')
	return varB[1]

#print(TupleComandSNMP('dollars','192.168.0.10','1.3.6.1.4.1.2021.11.9.0'))