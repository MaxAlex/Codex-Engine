#import wxversion
#wxversion.select('4.0')


# VAGUE PLANS- base control is a notebook with pages for notes/papers/groups
# Add-item keystroke opens an add dialog according to the open page
# Add dialogs will need to allow entry for references between items, so
# also make item-selector dialogs which show the same list of things as the main
# notebook pages.  These selector *controls* will also have to handle multiple
# item selection (although only one type of item per field, I think.)

# Its probably best to also have (a) class(es) for items themselves, generated
# upon loading data from the disk database.  Caution in regards to adding/deleting
# items to not put the database out of sync, but there has to be an Elegant Solution
# for that sort of thing?


import wx
import wx.lib.mixins.listctrl as listmix
import os
import time
import sqlite3 as sqlite

#DATABASE_FILE = r'\\rc-data1\blaise\ms_data_share\Max\testdb.sqlite'
DATABASE_FILE = os.path.join(os.path.realpath(__file__), 'testdb.sqlite')
ONTOLOGY_FILE = os.path.join(os.path.realpath(__file__), 'ontological.txt')

SEPARATOR = '|||'



def get_current_time(): # In epoch format.
    return time.time()
def epoch_to_display(epochtime):
    try:
        return time.strftime('%d/%m/%y', time.gmtime(epochtime))
    except:
        return str(epochtime)
def get_epoch_for_time_ago(days):
    return get_current_time - (60*60*24*days)
    



def parse_ontology(ontofile):
    ontodata = open(ontofile).read().split('#')
    things = {}
    for desc in ontodata:
        lines = desc.split('\n')
        assert lines[0].split()[0] == 'TYPE', lines
        thingname = lines[0].split()[1]
        thing = []
        for line in lines[1:]:
            cmd, atts = line.split()
            thing.append((cmd, atts.split('|')))
        things[thingname] = thing
    return things
CURRENT_ONT = parse_ontology(ONTOLOGY_FILE)


DATAKIND_STORAGES = {"smalltext" : 'text',
                     "text" : 'text',
                     "datetime" : 'int'}
def initialize_database(db_file, thing_descs):
    connection = sqlite.connect(db_file)
    cursor = connection.cursor()
    for thingname, attributes in thing_descs:
        tablename = thingname.lower() + '_table'
        memberstring = "("
        for mode, atts in attributes:
            if mode == 'HAS' and atts[0] == 'ID':
                memberstring += 'id int,'
            elif mode == 'HAS':
                label, dataname, datakind = atts
                memberstring += '%s %s,' % (dataname, DATAKIND_STORAGES[datakind])
            elif mode == 'LINKS':
                linkkind, label, dataname, count = atts
                memberstring += '%s text' % dataname
            elif mode == 'SHOWS':
                pass # Just determines what shows up on the item list.
            else:
                raise Exception, 'Parse error: %s' % str((mode, atts))
        memberstring += ')'
        table_command = "CREATE TABLE %s %s" % (tablename, memberstring)
        cursor.execute(table_command)
        cursor.commit()
    connection.close()
    print "Database initialized successfully."
if not os.path.exists(DATABASE_FILE):
    initialize_database(DATABASE_FILE, CURRENT_ONT)
DATA_CON = sqlite.connect(DATABASE_FILE)
DATA = DATA_CON.cursor()

# Retrieving a list of items would likely be faster if 
# not done one-per-query, but whatever.  Prototype!
def retreiveItemData(itemtype, idNum, fields):
    command = "SELECT %s FROM %s WHERE id = '%s'" % (', '.join(fields),
                                                     itemtype.lower(),
                                                     str(idNum))
    DATA.execute(command)
    return DATA.fetchall()[0]
    



def add_entry_to_database(db_cursor, entry_info):
    raise NotImplementedError

    
class NewItemDialog(wx.Dialog):
    def add_text_entry(self, title, defaulttext = ''):
        label = wx.StaticText(self, -1, title)
        ctrl = wx.TextCtrl(self, -1, defaulttext,
                           style = wx.TE_MULTILINE)
        box = wx.BoxSizer(orient = wx.VERTICAL)
        box.Add(label, flag = wx.ALIGN_LEFT)
        box.Add(ctrl, flag = wx.EXPAND)
        return ctrl.GetValue, box
    def add_small_text_entry(self, title, defaulttext = ''):
        label = wx.StaticText(self, -1, title)
        ctrl = wx.TextCtrl(self, -1, defaulttext)
        box = wx.BoxSizer(orient = wx.HORIZONTAL)
        box.Add(label, flag = wx.ALIGN_LEFT)
        box.Add(ctrl, flag = wx.EXPAND)
        return ctrl.GetValue, box
    def add_itemselector(self, title, itemtype, itemcount,
                         defaultmembers = None):
        itemdog = SELECTOR_TYPES[itemtype]
        label = wx.StaticText(self, -1, title)
        selector = ItemListPanel(self, itemtype, defaultmembers)
        def open_selector(self, evt):
            if itemdog.ShowModal() == wx.ID_OK:
                items = itemdog.GetItems()
                selector.addItems(items)
        
        button = wx.Button(self, -1, 'Select')
        self.Bind(wx.EVT_BUTTON, open_selector, button)
        
        return label, selector.GetMemberIds, button
    
    def __init__(self, thingname, thing_desc, thing_info):
        wx.Dialog.__init__(self, parent, -1,
                           title = "Adding New %s" % thingname)
        self.ctrls = {}
        sizer = wx.BoxSizer()
        for mode, atts in thing_desc:
            if mode == 'HAS' and len(atts) != 1:
                label, dataname, datakind = atts
                if datakind == 'smalltext':
                    ctrl, box = self.add_small_text_entry(label,
                                                          thing_info[label])
                elif datakind == 'text':
                    ctrl, box = self.add_text_entry(label,
                                                    thing_info[label])
                elif datakind == 'datetime':
                    # This could helpfully be updated to a datetime-specific
                    # entry control.
                    ctrl, box = self.add_small_text_entry(label,
                                                          thing_info[label])
                else:
                    raise Exception, datakind
            elif mode == 'LINKS':
                linkkind, label, dataname, count = atts
                ctrl, box = self.add_itemselector(label, linkkind, count,
                                                  thing_info[label])
            else:
                assert atts == 'ID' or mode == 'SHOW', (mode, atts)
            self.ctrls[dataname] = ctrl
            sizer.Add(box)
            sizer.Add(wx.StaticLine(style = wx.LI_HORIZONTAL))
        
        self.SetSizerAndFit(sizer)
        self.Show()
    
    def MakeItem()
        

    
    
    
    
    
    
    
    
class MixedListCtrl(listmix.ListCtrlAutoWidthMixin, wx.ListCtrl):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
    


class ItemListPanel(wx.Panel):
    def __init__(self, parent, itemtype, listmembers):
        wx.Panel.__init__(self, parent = parent, id = -1, *args, **kwargs)        
        sizer = wx.BoxSizer()
        self.list = MixedListCtrl(self, -1, style = wx.LC_REPORT)

        item_ont = CURRENT_ONT[itemtype]
        item_atts = [x[1] for x in item_ont if x[0] == 'HAS' or x[0] == 'LINKS']
        column_names, data_names = zip(*item_atts)[:2]
        
        for colname in column_names:
            self.list.AppendColumn(colname)
        for listmember in listmembers:
            memberdata = retrieveItemData(itemtype, listmember['id'], data_names)
            # May want to add some extra formatting (string shortening...) here.
            self.list.Append(map(str, memberdata))
            
        self.SetSizerAndFit(sizer)
        
        self.list.SetSize(self.GetSize()) # Probably obsolete?

    def GetMemberIds(self):
        # Return ID attribute of all displayed entries, for use in 
        # NewItemDialog.
        pass
    def GetSelectedMemberIds(self):
        # For use in ItemSelector-contained instances.
        pass

class ItemSelector(wx.Dialog):
    # Contains an ItemListPanel that lists all entries of the specified
    # type in the database.
    pass
        
        
# "Display"s and "ItemSelector" should be the same thing.
class MainDisplay(wx.Frame):
    def __init__(self, parent, id = -1):
        wx.Frame.__init__(self, parent, id, name = "Codex Engine", size = (700, 800))
        
        self.LoadDatabase()
        
        self.panel = wx.Panel(self)
        self.note = wx.Notebook(self.panel, size = (700, 800))

        sizer = wx.BoxSizer()
        sizer.Add(self.note, flag = wx.EXPAND)
        self.panel.SetSizerAndFit(sizer)
        
        self.notepage = NoteDisplay(self.note, self.data)
        self.paperpage = PaperDisplay(self.note, self.data)
        self.grouppage = GroupDisplay(self.note, self.data)
        for page, text in [(self.notepage, "Notes"), 
                           (self.paperpage, "Papers"),
                           (self.grouppage, "Groups")]:
            self.note.AddPage(page, text)  
            
        self.Bind(wx.EVT_CHAR_HOOK, self.processKeypress)
        self.Bind(wx.EVT_SIZE, self.beTheRightFrikkinSizeYouPiecesOfJunk)
        self.Show()

        self.beTheRightFrikkinSizeYouPiecesOfJunk(None)
        print "FOO"
    
    def beTheRightFrikkinSizeYouPiecesOfJunk(self, event):
        self.panel.SetSize(self.GetSize())
        self.note.SetSize(self.panel.GetSize())
        for page in [self.notepage, self.paperpage, self.grouppage]:
            page.list.SetSize(page.GetSize())        
    
    def LoadDatabase(self):
        self.connection = sqlite.connect(DATABASE_FILE)
        self.data = self.connection.cursor()

    def processKeypress(self, event):
        key = event.GetKeyCode()
        ctrled = wx.GetKeyState(wx.WXK_CONTROL)
        if ctrled:
            print "ctrl-%s" % key
        else:
            print str(key)
        
        if key == 86 and ctrled: # ctrl-v
            self.openNewItemDialog()
        elif key == 69 and ctrled: # ctrl-e
            self.openCurrentItemDialog()
        elif key == 68 and ctrled: # ctrl-d
            self.openDeleteItemDialog()
            
    
    def openNewItemDialog(self):
        target = self.note.GetCurrentPage()
        if isinstance(target, NoteDisplay):
            dialog = NewNoteDialog(self)
        elif isinstance(target, PaperDisplay):
            dialog = NewPaperDialog(self)
        elif isinstance(target, GroupDisplay):
            dialog = NewGroupDialog(self)
        else:
            raise Exception
        
        if dialog.ShowModal() == wx.ID_OK:
            target.AddNewItem(dialog.ItemData)
    
    def openCurrentItemDialog(self):
        target = self.note.GetCurrentPage()
        index = target.list.GetFirstSelected()
        if index < 0: return
        else:
            item = target.list
        if isinstance(target, NoteDisplay):
            dialog = NoteInfoDialog(item)
        elif isinstance(target, PaperDisplay):
            dialog = PaperInfoDialog(item)
        elif isinstance(target, GroupDisplay):
            dialog = GroupInfoDialog(item)
        else:
            raise Exception            
        
        dialog.ShowModal()
        


if __name__ == '__main__':
    app = wx.App(0)
    if not os.path.exists(DATABASE_FILE):
        filedog = wx.FileDialog(None, "Database file not found, please locate",
                                style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if filedog.ShowModal() == wx.ID_OK:
            DATABASE_FILE = filedog.GetPath()
    if os.path.exists(DATABASE_FILE):
        MainDisplay(None)
        app.MainLoop()

#if __name__ == '__main__':
    #initialize_database(DATABASE_FILE)
            
            
        
        
        