#
# POC FTP Browser for Enigma2
#

from FTPBrowser import FTPBrowser

ftpbrowser = None

def createSingleton(session):
	global ftpbrowser
	if not ftpbrowser:
		ftpbrowser = session.instantiateDialog(FTPBrowser)
		return False
	return True

def main(session, **kwargs):
	createSingleton(session)
	session.execDialog(ftpbrowser)

def filescan_chosen(session, item):
	if item:
		createSingleton(session)
		ftpbrowser.connect(item[1])
		session.execDialog(ftpbrowser)

def filescan_open_connected(res, items, session, **kwargs):
	if res:
		ftpbrowser.disconnect()
		filescan_open(items, session, **kwargs)

def filescan_open(items, session, **kwargs):
	if createSingleton(session) and ftpbrowser.ftpclient:
		from Screens.MessageBox import MessageBox
		from Tools.BoundFunction import boundFunction

		session.openWithCallback(
			boundFunction(filescan_open_connected, items, session, **kwargs),
			MessageBox,
			_("There already is an active connection.\nDo you want to abort it?"),
			type = MessageBox.TYPE_YESNO
		)
		return

	Len = len(items)
	if Len > 1:
		from Screens.ChoiceBox import ChoiceBox
		from Tools.BoundFunction import boundFunction

		session.openWithCallback(
			boundFunction(filescan_chosen, session),
			ChoiceBox,
			_("Which server do you want to connect to?"),
			[(item, item) for item in items]
		)
	elif Len:
		filescan_chosen(items[0])

def filescan(**kwargs):
	from Components.Scanner import Scanner, ScanPath

	# Overwrite checkFile to detect remote files
	class RemoteScanner(Scanner):
		def checkFile(self, file):
			return file.path.startswith("ftp://")

	return [
		RemoteScanner(
			mimetypes = None,
			paths_to_scan =
				(
					ScanPath(path = "", with_subdirs = False),
				),
			name = "Connect",
			description = _("Connect to FTP..."),
			openfnc = filescan_open,
		),
	]

def Plugins(**kwargs):
	from Plugins.Plugin import PluginDescriptor

	return [
		PluginDescriptor(
			name="FTPBrowser",
			description = _("A basic FTP client"),
			where = PluginDescriptor.WHERE_PLUGINMENU,
			fnc = main
		),
		PluginDescriptor(
			name = "FTPBrowser",
			where = PluginDescriptor.WHERE_FILESCAN,
			fnc = filescan
		),
	]