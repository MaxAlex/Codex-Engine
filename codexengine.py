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

DATABASE_FILE = r'\\rc-data1\blaise\ms_data_share\Max\testdb.sqlite'


NOTE_COLS = ['Body', 'Source', 'Reference(s)', 'Group(s)', 'Added']
PAPER_COLS = ['Title', 'Source', 'Author(s)', 'Publication Date', 'Group(s)', 'Description', 'Added', 'Read']
GROUP_COLS = ['Name', '# Members', 'Description', 'Added']

SEPARATOR = '|||'



SELECTOR_TYPES = {'Note':NoteSelector,
                  'Paper':PaperSelector,
                  'Group':GroupSelector}

def get_current_time(): # In epoch format.
    return time.time()
def epoch_to_display(epochtime):
    try:
        return time.strftime('%d/%m/%y', time.gmtime(epochtime))
    except:
        return str(epochtime)
def get_epoch_for_time_ago(days):
    return get_current_time - (60*60*24*days)
    


def initialize_database(db_file):
    connection = sqlite.connect(db_file)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE notes (id int, added text, body text, source text, target text, groups text)""")
    # ID is identifier number, body is the ntoe itself, source is title of source paper, target is list of 
    # relevant other things, groups is list of group names.
    cursor.execute("""CREATE TABLE papers (id int, title text, pubdate text, authors text, groups text, summary text, notes text, misc text, added text, read text)""")
    # ID is identifier number, title is paper title, source is name of journal or etc, authors are paper authors, groups is list of group
    # names, summary is written description of paper, misc is auxiliary data that can be gleaned from entry.
    cursor.execute("""CREATE TABLE groups (id int, name text, members text, description text, added text)""")
    # ID is identifier number, name is group name, members is list of paper titles and note ids, description is written summary.
    connection.commit()
    connection.close()
    
    
    
class NewItemDialog(wx.Dialog):
    def add_text_entry(self, title, defaulttext = ''):
        label = wx.StaticText(self, -1, title)
        ctrl = wx.TextCtrl(self, -1, defaulttext)
        return label, ctrl
    def add_itemselector(self, title, itemtype):
        itemdog = SELECTOR_TYPES[itemtype]
        label = wx.StaticText(self, -1, title)
        selector = ItemSelector(self, [])
        def open_selector(self, evt):
            if itemdog.ShowModal() == wx.ID_OK:
                items = itemdog.GetItems()
                selector.addItems(items)
        
        button = wx.Button(self, -1, 'Select')
        self.Bind(wx.EVT_BUTTON, open_selector, button)
        
        return label, selector, button
        
class NewNoteDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, title = "Adding New Note")
        
        
    
    
    
    
    
    
    
    
class MixedListCtrl(listmix.ListCtrlAutoWidthMixin, wx.ListCtrl):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
    


class ItemDisplay(wx.Panel):
    def __init__(self, parent, database, *args, **kwargs):
        wx.Panel.__init__(self, parent = parent, id = -1, *args, **kwargs)
        self.parent = parent
        self.db = database
        
        sizer = wx.BoxSizer()
        self.list = MixedListCtrl(self, -1, style = wx.LC_REPORT)
        sizer.Add(self.list, flag = wx.EXPAND)
        
        self.Bind(wx.EVT_KEY_DOWN, self.parent.GetParent().GetParent().processKeypress)
        self.SetSizerAndFit(sizer)
        
        self.list.SetSize(self.GetSize())
        print "FOO"
        #self.Populate()
        
        #listmix.ColumnSorterMixin.__init__(self, 3)
        

    def GetListCtrl(self):
        return self.list    
    #def Populate(self):
        #raise NotImplementedError, 'Implemented by note/paper/group displays.'

class NoteDisplay(ItemDisplay):
    def __init__(self, *args, **kwargs):
        ItemDisplay.__init__(self, *args, **kwargs)
        
        for col_name in NOTE_COLS:
            self.list.AppendColumn(col_name)        
        
        self.note_list = self.db.execute('SELECT * FROM notes').fetchall() + [(['test']*6)]
        self.note_list.sort(key = lambda x: x[0])
        for idnum, text, source, target, groups, added in self.note_list:
            targets = target.split(SEPARATOR)
            groups = groups.split(SEPARATOR)
            self.list.Append([text, source, ', '.join(targets), ', '.join(groups), epoch_to_display(added)])
        
    
class PaperDisplay(ItemDisplay):
    def __init__(self, *args, **kwargs):
        ItemDisplay.__init__(self, *args, **kwargs)
    
        for col_name in PAPER_COLS:
            self.list.AppendColumn(col_name) 
    
        self.paper_list = self.db.execute('SELECT * FROM papers').fetchall()
        self.paper_list.sort(key = lambda x: x[0])
        for idnum, title, authors, groups, description in self.paper_list:
            authors = authors.split(SEPARATOR)
            groups = groups.split(SEPARATOR)
            self.list.Append([title, ', '.join(authors), ', '.join(groups), description])
            
        
class GroupDisplay(ItemDisplay):
    def __init__(self, *args, **kwargs):
        ItemDisplay.__init__(self, *args, **kwargs)
        
        for col_name in GROUP_COLS:
            self.list.AppendColumn(col_name)        
    
        self.group_list = self.db.execute("SELECT * FROM groups").fetchall()
        self.group_list.sort(key = lambda x: x[0])
        for idnum, name, memberlist, description, added in self.group_list:
            membercount = len(memberlist.split(SEPARATOR))
            self.list.Append([idnum, membercount,
                              description, epoch_to_display(added)])
        
  



class ItemDialog(wx.Dialog):
    def __init__(self, parent, note_row = None, title = None):
        wx.Dialog.__init__(self, parent, -1, title = title)
    
    def textCtrl(self, labeltitle, labelname, defaultvalue):
        return (wx.StaticText(self, -1, labeltitle),
                wx.TextCtrl(self, -1, defaultvalue, name = labelname))


#class NoteInfoDialog(wx.ItemDialog):
    #def __init__(self, parent, note_row = None, title = None):
        #wx.ItemDialog.__init__(self, parent, -1, title = title)    
        
        #if note_row:
            
            
        
        #idnum_ws = self.textCtrl('')
        
        #gbs = wx.GridBagSizer(5, 5)
        
        
        

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
            
            
        
        
        