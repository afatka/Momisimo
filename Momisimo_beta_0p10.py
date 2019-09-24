from tkinter import *
from tkinter.ttk import *
import tkinter.filedialog, tkinter.messagebox, os, re, sys, textwrap, warnings, random #copy
import xml.etree.ElementTree as etree
try: 
    import cPickle as pickle #import c implementation of pickle
except:
    import pickle #if cPickle isn't available load pickle


# try Tk.update() to force refresh
# or Tk.update_idletasks()

class Subcat(Frame):

    def __init__(self, input_subcat, defaults_xml, update_cat_grade, master=None):
        self.development = False
        self.isComplete = False
        # self.state = 1
        self.defaults_xml = defaults_xml
        self.update_cat_grade_total = update_cat_grade
        self.log('Starting Subcat')
        Frame.__init__(self, master)
        self.pack(side = 'top', fill = 'x', expand = 0, anchor = 'n')

        self.in_dict = self.build_subcat(input_subcat)
        self.createWidgets()
        self.build_rmb(input_subcat)

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    def build_rmb(self, input_subcat):
        self.log('build_RMB')

        self.rmb = []
        if input_subcat.findall('RMB'):
            self.log('found RMB in xml')
            for item in input_subcat.findall('RMB'):
                self.rmb.append((item.get('title'), item.text))

        if self.rmb != []:
            self.rmb_menu = Menu(self.user_comments_frame, tearoff = 0)
            for menu_item in self.rmb:
                # print('title: {}\ncomment: {}'.format(menu_item[0], menu_item[1]))
                self.rmb_menu.add_command(label = menu_item[0], command = lambda x = menu_item[1]:self.add_comment(x))

        self.user_comments_text.bind('<Button-2>', self.rmb_menu_popup)

    def add_comment(self, comment):
        self.log('add comment: {}'.format(comment))
        # print('add comment: {}'.format(comment))
        self.log('clear selection?')
        self.user_comments_text.selection_clear()
        self.log('clear')
        if self.user_comments == '':
            self.user_comments_text.insert('1.0', comment)
        else:
            self.user_comments_text.insert('end+1c', comment)
        self.update_user_comments()
#####
#####
#####
        # print('before update')
        self.update()
        # print('updated')
#####
#####
#####



    def rmb_menu_popup(self, event):
        self.log('RMB menu pop up')
        self.rmb_menu.post(event.x_root, event.y_root)

    def createWidgets(self):

        self.grade_entry = IntVar()
        self.slider_value = IntVar()
        self.radio_value = StringVar()
        self.slider_value.set(0)
        self.grade_entry.set(0)
        self.default_comments = ''
        self.user_comments = ''
        self.radio_value.set('Null')
        self._grade = { 'title': self.title, 
                        'weight': self.weight, 
                        'grade': self.grade_entry.get(), 
                        'defaults_comments': self.default_comments,
                        'user_comments': self.user_comments}
        self.base_width = 4
        self.number_of_radios = len(self.in_dict['SUBSECTION_INFO']['comments'].keys())
        self.grade_entry.trace('w', self.update_from_entry)
        
        slider_width = 300
        radio_width = self.base_width/2
        comment_width = int(300/7)
        
        self.subNotebook = Notebook(self)
        grade_frame = Frame(self, borderwidth = 2, relief = 'sunken')
        Label(grade_frame, text = self.in_dict['SUBSECTION_INFO']['title']).pack(side = 'top', fill = 'x')
        # grade_frame = Frame(self.subNotebook)
        entry_slider_frame = Frame(grade_frame)
        self.grade_widget = Entry(entry_slider_frame,  
                        width = self.base_width,
                        # xscrollcommand = self.update_from_entry,
                        textvariable = self.grade_entry,
                        validate = 'all',
                        validatecommand = self.entry_validation).pack(side = 'left')

        self.slider = Scale(entry_slider_frame, 
                        from_ = -100, 
                        to = 0, 
                        orient = HORIZONTAL,
                        length = slider_width,
                        variable = self.slider_value, 
                        command = self.update_from_slider).pack(side = 'left', fill = 'x', anchor = 'e', expand = 1)
        entry_slider_frame.pack(side = 'top', fill = 'x', anchor = 'center')

        radio_frame = Frame(grade_frame)
        for i in self.in_dict['LETTER_ORDER']:
            if i in self.in_dict['SUBSECTION_INFO']['comments'].keys():
                Radiobutton(radio_frame, 
                            variable = self.radio_value, 
                            value = i, 
                            text = i, 
                            width = radio_width, 
                            command = self.update_from_radio,).pack(side = 'left')
        radio_frame.pack(side = 'top', fill = 'x', expand = 1, anchor = 'center')

        self.user_comments_frame = Frame(self.subNotebook)
        user_comments_scroll = Scrollbar(self.user_comments_frame, 
                                command = self.update_user_comments)
        self.user_comments_text = Text(self.user_comments_frame, 
                            height = 5, 
                            width = comment_width,
                            background = '#d5d5d5',
                            border = 0,
                            wrap = 'word', 
                            yscrollcommand = user_comments_scroll.set)
        
        user_comments_scroll.pack(side = 'right', fill = 'y', anchor = 'e')
        self.user_comments_text.pack(side = 'left', fill = 'both', expand = 1)
        self.user_comments_text.bind('<Leave>', self.update_user_comments)
        self.user_comments_text.bind('<FocusOut>', self.update_user_comments)
        self.user_comments_frame.pack(side = 'top', fill = 'x', expand = 1)

        default_comments_frame = Frame(self.subNotebook)
        default_comments_scroll = Scrollbar(default_comments_frame, 
                                command = self.update_default_comments)
        self.default_comments_text = Text(default_comments_frame, 
                            height = 5, 
                            width = comment_width,
                            background = '#d5d5d5',
                            border = 0,
                            wrap = 'word', 
                            yscrollcommand = default_comments_scroll.set, 
                            state = DISABLED)
        
        default_comments_scroll.pack(side = 'right', fill = 'y', anchor = 'e')
        self.default_comments_text.pack(side = 'left', fill = 'both', expand = 1)
        default_comments_frame.pack(side = 'top', fill = 'x', expand = 1)


        # self.subNotebook.add(grade_frame, text = self.in_dict['SUBSECTION_INFO']['title'])

        grade_frame.pack(side = 'top', fill = 'x', expand = 1, anchor = 'n')

        self.subNotebook.add(self.user_comments_frame, text = 'Comments')
        self.subNotebook.add(default_comments_frame, text = 'Defaults')

        self.subNotebook.pack(side = 'top', fill = 'x', expand = 1, anchor = 'n')        

    def update_user_comments(self, *args):
        # self.log('user comments args: {}'.format(args))
        self.user_comments = self.user_comments_text.get('1.0', 'end-1c')
        # self.log('ucomments: {}'.format(self.user_comments))

    def update_default_comments(self, *args):
        # self.log('default comments args: {}'.format(args))
        self.default_comments = self.default_comments_text.get('1.0', 'end-1c')
        # self.log('dcomments: {}'.format(self.default_comments))

    def update_from_slider(self, *args):
        
        self.grade_entry.set(abs(self.slider_value.get())) #############################
        self.int_to_radio(abs(self.slider_value.get()))
        self.update_cat_grade_total()
        self.set_isComplete()

    def update_from_entry(self, *args):
        self.log('entry Args: {}'.format(args))

        try: 
            g = self.grade_entry.get()
            self.slider_value.set(-g)
            self.int_to_radio(g)
            self.update_cat_grade_total()
            self.set_isComplete()
        except ValueError:
            self.log('Value Error: Pass')

    def entry_validation(self, *args):
        self.log('entry_validation Args: {}'.format(args))
        
        try: 
            self.log('g: {}'.format(self.grade_entry.get()))
            g = self.grade_entry.get()
        except ValueError:
            # self.grade_entry.set(0)
            g = 0

        if 0<= g <=100:
            self.log('validate true: {}'.format(g))
            return True
        else:
            self.log('validate false: {}'.format(g))
            return False

    def int_to_radio(self, int_grade):
        # self.log('int_to_radio: {}'.format(int_grade))
        for i in self.in_dict['LETTER_ORDER']:
            if i in self.in_dict['SUBSECTION_INFO']['comments'].keys():
                # self.log('{} found.'.format(i))
                if int_grade >= self.in_dict['LETTER_VALUE'][i]:
                    # self.log('{} >= {}'.format(int_grade, self.in_dict['LETTER_VALUE'][i]))
                    self.radio_value.set(i)
                    self.update_placed_default_comments(i)
                    break
                self.radio_value.set(i)
                self.update_placed_default_comments(i)

    def nuke(self, value):
        self.log('nuke sub cat')
        self.grade_entry.set(int(value))
        self.update_from_entry()

    @property
    def grade(self):
        self.log('grade getter')
        self._grade = {'title': self.title, 
                        'weight': self.weight, 
                        'grade': self.grade_entry.get(), 
                        'defaults_comments': self.default_comments,
                        'user_comments': self.user_comments}
        return self._grade

    @grade.setter
    def grade(self, grade_dict):
        self.log('grade setter')
        if grade_dict['title'] == self.title:

            self.grade_entry.set(grade_dict['grade'])
            self.update_from_entry()

            self.user_comments_text.delete('1.0', 'end-1c')
            self.user_comments_text.insert('1.0', grade_dict['user_comments'])
            self.update_user_comments()
            # self.user_comments = grade_dict['user_comments']
        else:
            warnings.warn('title NO MATCH: {} : {}'.format(self.title, grade_entry['title']))

    def update_placed_default_comments(self, key):
        # self.log('update default comments in box: {}'.format(key))
        self.default_comments_text.config(state = NORMAL)
        self.default_comments_text.delete('1.0', 'end-1c')
        # self.log('dcoms deleted')
        self.default_comments_text.insert('1.0', self.in_dict['SUBSECTION_INFO']['comments'][key])
        # self.log('dcoms populated')
        # self.log('dcom: {}'.format(self.in_dict['SUBSECTION_INFO']['comments'][key]))
        self.update_default_comments()
        self.default_comments_text.config(state = DISABLED)

    def update_from_radio(self, *args):
        # self.log('radio Args: {}'.format(args))
        grade_value = self.in_dict['LETTER_VALUE'][self.radio_value.get()]
        # self.log('{}:{}'.format(self.radio_value.get(), grade_value))
        self.slider_value.set(-grade_value)
        self.grade_entry.set(grade_value)
        self.update_cat_grade_total()
        self.update_placed_default_comments(self.radio_value.get())
        self.set_isComplete()

    def set_isComplete(self):
        self.log('set {} as complete'.format(self.title))
        self.isComplete = True

    def reset(self):
        self.log('reset {}'.format(self.title))
        self.slider_value.set(0)
        self.grade_entry.set(0)
        self.default_comments = ''
        self.user_comments = ''
        self.radio_value.set('Null')

        self.default_comments_text.config(state = NORMAL)
        self.default_comments_text.delete('1.0', 'end-1c')
        self.default_comments_text.config(state = DISABLED)

        self.user_comments_text.delete('1.0', 'end-1c')

        self.isComplete = False
        self.subNotebook.select(0)

    def build_subcat(self, subcat):
        self.log('temp subcat build')
        subcat_dict = {}
        subcat_dict['LETTER_ORDER'] = [
            'A+', 'A', 'A-',
            'B+', 'B', 'B-',
            'C+', 'C', 'C-',
            'D+', 'D', 'D-',
            'F+', 'F', 'F-' ]

        subcat_dict['LETTER_VALUE'] = {}
        xml_gradeValues = self.defaults_xml.find('gradeValue')
        for letter in subcat_dict['LETTER_ORDER']:
            l = re.sub('\\+', 'plus', letter)
            val = None
            c = None
            try:
                c = subcat.find('gradeComment').find(l) #Should 'l' here be letter?
            except AttributeError:
                pass
            if c != None:
                try:
                    val = xml_gradeValues.find(l).text #Should 'l' here be letter?
                except AttributeError:
                    pass
                if val != None:
                    # self.log('val: {}'.format(val))
                    subcat_dict['LETTER_VALUE'][letter] = int(val)

        subcat_dict['SUBSECTION_INFO'] = {}
        title = subcat.get('title')
        if title == None:
            title = subcat.find('title').text
        subcat_dict['SUBSECTION_INFO']['title'] = title
        self.title = title

        weight = subcat.get('weight')
        if weight == None:
            weight = subcat.find('weight').text
        subcat_dict['SUBSECTION_INFO']['weight'] = weight
        self.weight = int(weight)

        subcat_dict['SUBSECTION_INFO']['comments'] = {}
        for k in subcat_dict['LETTER_VALUE']:
            l = re.sub('\\+', 'plus', k)
            # self.log('key: {}\nl: {}'.format(k, l))
            subcat_dict['SUBSECTION_INFO']['comments'][k] = subcat.find('gradeComment').find(l).text

        return subcat_dict

    def log(self, message, prefix = 'Subcat: '):
        if self.development:
            print('{}{}'.format(prefix, message))

class Maincat(Frame):

    def __init__(self, maincat_xml, defaults_xml, master = None):
        self.development = False
        # self.isComplete = False
        self.log('Starting Maincat')
        self.gradeInt_updater = None
        self.gradeTotal_updater = None
        self.maincat_xml = maincat_xml
        self.defaults_xml = defaults_xml
        self.main_cat_grade = 0

        self.cat_grade_value = IntVar()

        self.title = self.maincat_xml.get('title')
        if self.title == None:
            self.title = self.maincat_xml.find('title').text

        self.weight = self.maincat_xml.get('weight')
        if self.weight == None:
            self.weight = self.maincat_xml.find('weight').text
    
        # the scrolling frame canvas stuff comes, pretty much directly 
        # from 
        # http://stackoverflow.com/a/3092341/5079170
        Frame.__init__(self, master)
        
        self.canvas = Canvas(self, background = '#ededed', 
                                    borderwidth = 0, 
                                    selectborderwidth = 0,
                                    highlightthickness=0)
        self.subcat_frame = Frame(self.canvas)
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=1)
        self.canvas_win = self.canvas.create_window((4,4), window=self.subcat_frame, anchor="nw", 
                                  tags="self.subcat_frame")

        self.subcat_frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind('<Configure>', self.onFrameWidth)

        self.build_highnotes(self.subcat_frame)
        self.build_subcats(self.subcat_frame)

        self.pack(side = 'top', fill = 'both', expand = 1)

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    def onFrameWidth(self, event):
        '''change width of canvas window'''
        # self.log('change width')
        self.canvas.itemconfig(self.canvas_win, width = event.width)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompas the inner frame'''
        # self.log('...{}'.format(event.width))
        self.canvas.configure(scrollregion = self.canvas.bbox('all'))
        # self.log('fire onFrameConfigure')

    def build_highnotes(self, parent):
        self.log('build highnotes')
        self.highnotes_comments = ''
        self.highnotes_toggleframe = ToggleFrame(self.subcat_frame)
        self.highnotes_frame = Frame(self.highnotes_toggleframe.exp_frame)
        highnotes_scroll = Scrollbar(self.highnotes_frame, 
                                    command = self.update_highnotes)
        self.highnotes_text = Text(self.highnotes_frame, 
                        height = 5, 
                        width = int(300/7),
                        background = '#d5d5d5',
                        border = 0,
                        wrap = 'word', 
                        yscrollcommand = highnotes_scroll.set)

        highnotes_scroll.pack(side = 'right', fill = 'y')
        self.highnotes_text.pack(side = 'left', fill = 'both', expand = 1)
        self.highnotes_text.bind('<Leave>', self.update_highnotes)
        self.highnotes_text.bind('<FocusOut>', self.update_highnotes)
        self.highnotes_frame.pack(side = 'top', fill = 'x', expand = 1)

    def update_highnotes(self, *args):
        self.log('update highnotes')
        self.highnotes_comments = self.highnotes_text.get('1.0', 'end-1c')

    def load_highnotes(self, highnotes):
        self.log('set highnotes')
        self.reset_highnotes()

        self.highnotes_text.insert('1.0', highnotes)

    def build_subcats(self, parent):
        self.subs = []
        for sub in self.maincat_xml.findall('subcategory'):
            self.subs.append(Subcat(sub, self.defaults_xml, self.update_cat_grade_total, master = parent))

    def update_cat_grade_total(self):
        self.log('update category grade total')
        grade_total = 0
        for sub in self.subs:
            # self.log('grade_entry: {}'.format(sub.grade_entry.get()))
            # self.log('weight: {}'.format(sub.weight))
            grade_total += ((sub.grade_entry.get() * sub.weight)/100)
        self.log('{} Grade Total: {}'.format(self.title, grade_total))
        self.main_cat_grade = grade_total
        if self.gradeInt_updater is not None:
            self.gradeInt_updater(self.title, self.main_cat_grade)
        if self.gradeTotal_updater is not None: 
            self.gradeTotal_updater()

    def reset(self):
        self.log('reset {}'.format(self.title))
        self.reset_highnotes()
        for sub in self.subs: 
            sub.reset()
        self.update_cat_grade_total()
        self.canvas.yview('moveto', '0')

    def nuke(self):
        self.log('nuke all incomplete sections')
        for sub in self.subs:
            if not sub.isComplete:
                sub.nuke(0)

    def reset_highnotes(self):
        self.log('reset highnotes')
        self.highnotes_comments = ''
        self.highnotes_text.delete('1.0', 'end-1c')

    def isComplete(self):
        self.log('Check if {} is complete'.format(self.title))
        incomplete_subs = []
        return_list = [self.title,]
        for sub in self.subs:
            if not sub.isComplete:
                incomplete_subs.append(sub.title)
        if incomplete_subs != []:
            return_list.append(incomplete_subs)
            return return_list
        return incomplete_subs

    @property
    def grade(self):
        self.log('{} grade getter'.format(self.title))
        
        sub_grades = []

        for sub in self.subs:
            sub_grades.append(sub.grade)

        self._grade = {'title' : self.title, 
                        'weight' : self.weight,
                        'grade' : self.main_cat_grade,
                        'highnotes' : self.highnotes_comments,
                        'subs' : sub_grades}

        return self._grade

    @grade.setter
    def grade(self, grade_dict):
        self.log('{} grade setter'.format(self.title))
        if grade_dict['title'] == self.title:

            self.load_highnotes(grade_dict['highnotes'])
            self.update_highnotes()

            for loaded_sub in grade_dict['subs']:
                for sub in self.subs: 
                    if loaded_sub['title'] == sub.title:
                        sub.grade = loaded_sub
        else: 
            warnings.warn('title NO MATCH: {} : {}'.format(self.title, grade_entry['title']))
     
    def stop(self):
        raise ValueError('STAAAHP!')

    def log(self, message, prefix = 'Maincat: '):
        if self.development:
            print('{}{}'.format(prefix, message))

class ToggleFrame(Frame):

    def __init__(self, master = None, *args, **kwargs):
        self.development = False
        self.log('Toggle Frame init')

        Frame.__init__(self, master)
        self.pack(side = 'top', fill = 'x', expand = 1)

        self.vis = True
        # self.vis.set(1)

        self.title_frame = Frame(self)
        self.title_frame.pack(side = 'top', fill = 'x', expand = 1)

        Label(self.title_frame, text = 'Highnotes').pack(side = 'left', fill = 'x', expand = 1)
        # self.expand_button = Checkbutton(self.title_frame, width = 2, text = '+', variable = self.vis, 
        #                                      command = self.toggle_vis)
        self.expand_button = Button(self.title_frame, width = 2, text = '+', command = self.toggle_vis)
        self.expand_button.pack(side = 'left')

        self.exp_frame = Frame(self)

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    def toggle_vis(self):
        self.log('Toggle vis')
        # self.log('vis: {}'.format(self.vis.get()))
        # self.log('vis: {}'.format(bool(self.vis.get())))

        if self.vis:
            self.exp_frame.pack(fill = 'x', expand = 1)
            self.expand_button.config(text = '-')
            self.vis = not self.vis
        else:
            self.exp_frame.forget()
            self.expand_button.config(text = '+')
            self.vis = not self.vis

    def log(self, message, prefix = 'ToggleFrame: '):
        if self.development:
            print('{}{}'.format(prefix, message))

class GradeIntFields(Frame):

    def __init__(self, mains, boxes, equation, updater, master = None):
        self.development = False
        self.log('GradeIntFields Started')
        self.equation = equation
        self.updater = updater
        Frame.__init__(self, master)
        self.pack(side = 'top', fill = 'x',expand = 0)

        self.grade_fields = [] 
        self.grade_boxes = []
        for main in mains:
            self.grade_fields.append(self.create_grade_field(main.title))
        for box in boxes:
            gbox = self.create_grade_field(box.get('title'), bind = True)
            self.grade_fields.append(gbox)
            self.grade_boxes.append((gbox[0], gbox[1], box.text))#title, var, text

        self.grade_total_intField = self.create_grade_field('Total')

        self.pack(side = 'top', expand = 0)

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    @property
    def grade(self):
        self.log('grade getter')
        self._grade = []
        if self.grade_boxes != []:
            for box in self.grade_boxes:
                box_dict = {'title' : box[0],
                            'grade' : box[1].get()} #generate a dictionary for consistency.
                self._grade.append((box[0], box[1].get(), box[2], box_dict)) #title, grade, text
        return self._grade

    @grade.setter
    def grade(self, grade_dict):
        self.log('grade setter')
        for box in self.grade_boxes:
            if box[0] == grade_dict['title']:
                box[1].set(grade_dict['grade'])
            else:
                warnings.warn('title NO MATCH: {}'.format(grade_dict['title']))

    def reset(self):
        self.log('reset boxes')
        for gradeField in self.grade_fields:
            gradeField[1].set(int(0))

    def update_grade_int(self, main_cat_name, grade_value):
        # self.log('updating grade int field')
        for gradeField in self.grade_fields:
            if main_cat_name == gradeField[0]:
                # self.log('{} found'.format(main_cat_name))
                gradeField[1].set(int(grade_value))

    def update_grade_total(self, title_weight_tuple):
        self.log('update grade total')
        grade = 0
        equation = self.equation
        for gradefield in self.grade_fields:
            # self.log('\nTitle: {} \nfield: {}'.format(gradefield[0], gradefield[2]))
            # self.log('\n\nequation: \n{}\n\n'.format(equation))
            section_match = [x for x in title_weight_tuple if x[0] == gradefield[0]]
            if section_match != []:
                section_match = section_match[0]
                # self.log('section_match: {}'.format(section_match))
                # self.log('replace: {}'.format(gradefield[0]))
                equation = equation.replace(gradefield[0][:3], str(((gradefield[1].get() * int(section_match[1])) / 100)))
            elif gradefield[0] != 'Late':
                # self.log('{} != \'Late\''.format(gradefield[0]))
                equation = equation.replace(gradefield[0][:3], str(gradefield[1].get()))
            else: 
                # self.log('equal Late')
                equation = equation.replace(gradefield[0], str(gradefield[1].get()))

        grade = eval(equation)
        if grade < 0:
            grade = 0
        self.grade_total_intField[1].set(int(grade))

    def create_grade_field(self, input_label, bind = False):
        label_width = 4
        field_width = 3
        grade_var = IntVar()
        grade_var.set(0)

        field_frame = Frame(self)
        if input_label == 'Late':
            field_label = Label(field_frame, width = field_width,text = input_label[:4])
        else:
            field_label = Label(field_frame, width = field_width,text = input_label[:3])
        field_label.pack(side = 'left', expand = 0)
        field_int = Entry(field_frame, width = label_width, textvariable = grade_var)
        field_int.pack(side = 'right', expand = 0)

        field_frame.pack(side = 'top', fill = 'x', expand = 0)

        if bind:
            field_int.bind('<Leave>', self.updater)
            field_int.bind('FocusOut', self.updater)

        return (input_label, grade_var, field_int)

    def log(self, message, prefix = 'Grade Ints: '):
        if self.development:
            print('{}{}'.format(prefix, message))

class FileManager(Frame):

    def __init__(self, file_types_from_xml, master = None):
        self.development = False
        self.file_types_from_xml = file_types_from_xml

        Frame.__init__(self, master)
        self.pack(side = 'top', fill = 'x', expand = 0)

        self.loaded_files = []
        self.active_file = ''
        self.completed_files = []
        self.input_dir = []

        self.file_queue = ListBoxWithScroll(self)
        self.completed_queue = ListBoxWithScroll(self)

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    def cycle_file(self):
        self.log('cycle the files: \n active > completed. \nloaded to active.')
        if self.active_file != '':
            self.completed_files.append(self.active_file)
        if len(self.loaded_files) != 0:
            self.active_file = self.loaded_files.pop(0)
        else: 
            self.active_file = 'end of queue'

        self.file_queue.update(self.loaded_files)
        self.completed_queue.update(self.completed_files)

    def load(self, *args):

        if args:
            dirs = args[0]
            for d in dirs:
                self.input_dir.append(d)

        self.log('load some files of type: {}'.format(self.file_types_from_xml))

        fileTypes = [x.strip(' ') for x in self.file_types_from_xml.split(',')]
        self.log('fileType: {}'.format(fileTypes))
        if not args:
            self.input_dir.append(tkinter.filedialog.askdirectory(parent = self, mustexist = True))
        self.log('input dir: \n{}'.format(self.input_dir))

        self.found_files = []
        for d in self.input_dir:
            self.found_files.extend(self.fileFinderOSWalk(d, tuple(fileTypes)))
        self.log('found {} files'.format(len(self.found_files)))

        for file in self.found_files:
            if file not in self.loaded_files:
                self.loaded_files.append(file)
            else:
                warnings.warn("File already in queue: \n{}".format(file))
            if file in self.completed_files:
                self.completed_files.remove(file)

        self.file_queue.update(self.loaded_files)
        self.completed_queue.update(self.completed_files)

    def load_file_from_pickle(self, path_to_pickle):
        self.log('load from pickle')
        pickle_companion = self.find_pickle_companion(path_to_pickle)

        for file in pickle_companion:
            self.loaded_files.append(file)
        self.file_queue.update(self.loaded_files)

    def not_implemented(self, title):
        self.log('not implemented')
        print('''

                
                {}***{}***
                ***NOT IMPLEMENTED***{}


                '''.format(color.BOLD, title, color.END))

    def find_pickle_companion(self, path_to_pickle):
        self.log('find pickle companion file')
        search_path, filename = os.path.split(path_to_pickle)
        filename = os.path.splitext(filename)[0]
        self.input_dir.append(search_path)
        fileTypes = tuple([x.strip(' ') for x in self.file_types_from_xml.split(',')])

        pickle_companion = []

        #recursion protection
        directoryDepth = 0
        maximum_recursion = 8

        for directoryName, subDirectoryName, fileList in os.walk(search_path):
            #janky recursion protection
            if directoryDepth == 0:
                directoryDepth = len(directoryName.split(os.sep))
            if len(directoryName.split(os.sep)) - directoryDepth >= maximum_recursion:
                warnings.warn('os.walk recursion break triggered')
                break

            for item in fileList:
                if (os.path.splitext(item)[0] == filename) and item.endswith(fileTypes):
                    pickle_companion.append(os.path.join(directoryName, item))

        return pickle_companion

    def check_for_active(self):
        self.log('check for active file')
        if self.active_file == '':
            raise Exception('No active file.')

    def skip_active(self):
        self.log('skip active file')
        self.check_for_active()
        self.loaded_files.append(self.active_file)
        self.active_file = ''
        self.cycle_file()

    def sort_alphabetical(self):
        self.log('sort alphabetical')
        # self.log('files:\n{}'.format(self.loaded_files))
        self.loaded_files.sort( key=lambda x:x.split(os.sep)[-1].lower())
        # self.log('Sorted files:\n{}'.format(self.loaded_files))
        self.file_queue.update(self.loaded_files)

    def send_to_next(self):
        self.log('send to next')
        self.log('selected: {}'.format(self.file_queue.selection))
        sel = self.file_queue.selection
        sel.reverse()
        temp = []
        if sel != []:
            for i in sel:
                f = self.loaded_files.pop(i)
                temp.append(f)
            self.log('temp: {}'.format(temp))
            for f in temp: 
                self.loaded_files.insert(0, f)
            self.log('loaded: {}'.format(self.loaded_files))
            self.file_queue.update(self.loaded_files)

    def send_to_last(self):
        self.log('send_to_last')
        self.log('selected: {}'.format(self.file_queue.selection))
        sel = self.file_queue.selection
        sel.reverse()
        if sel != []:
            for i in sel:
                f = self.loaded_files.pop(i)
                self.loaded_files.append(f)
            self.file_queue.update(self.loaded_files)
            # self.completed_queue.update(self.completed_files)

    def remove_file(self):
        self.log('Remove file')
        queued_count = len(self.file_queue.selection)
        completed_count = len(self.completed_queue.selection)
        confirm_message = 'Please confirm file removal.'
        if queued_count != 0:
            if queued_count == 1:
                confirm_message += '\n{} Queued file.'.format(queued_count)
            else:
                confirm_message += '\n{} Queued files.'.format(queued_count)
        if completed_count != 0:
            if completed_count == 1:
                confirm_message += '\n{} Completed file.'.format(completed_count)
            else:
                confirm_message += '\n{} Completed files.'.format(completed_count)

        if queued_count + completed_count != 0:
            if tkinter.messagebox.askokcancel('Confirm Removal', confirm_message):
                self.log('confirmed.')
                if queued_count != 0:
                    sel = self.file_queue.selection
                    sel.reverse()
                    for i in sel:
                        self.loaded_files.pop(i)
                    self.file_queue.update(self.loaded_files)
                if completed_count != 0:
                    sel = self.completed_queue.selection
                    sel.reverse()
                    for i in sel:
                        self.completed_files.pop(i)
                    self.completed_queue.update(self.completed_files)

            else: 
                self.log('canceled')
        else: 
            raise Exception('No files selected for removal')

    def mark_as_complete(self):
        self.log('mark_as_complete')
        self.log('selected: {}'.format(self.file_queue.selection))
        sel = self.file_queue.selection
        sel.reverse()
        if sel != []:
            for i in sel:
                f = self.loaded_files.pop(i)
                self.completed_files.append(f)
            self.file_queue.update(self.loaded_files)
            self.completed_queue.update(self.completed_files)

    def add_to_queue(self):
        self.log('add_to_queue')
        self.log('selected: {}'.format(self.completed_queue.selection))
        sel = self.completed_queue.selection
        sel.reverse()
        if sel != []:
            for i in sel:
                f = self.completed_files.pop(i)
                self.loaded_files.append(f)
            self.file_queue.update(self.loaded_files)
            self.completed_queue.update(self.completed_files)

    def grade_now(self):
        self.log('grade now')
        self.send_to_next()
        self.skip_active()

    def sort_modified_date(self):
        self.log('Sort by modified')
        # self.check_for_active()
        self.loaded_files.sort( key=lambda x: os.stat(x).st_mtime)
        self.file_queue.update(self.loaded_files)

    def sort_reversed(self):
        self.log('reverse the order')
        # self.check_for_active()
        self.loaded_files.reverse()
        self.file_queue.update(self.loaded_files)

    def pickle_filter(self):
        self.log('pickle filter')
        remove_files = []
        for f in self.loaded_files:
            pickle_file = os.path.splitext(f)[0] + '.mgs'
            # print('pickle file: {}'.format(pickle_file))
            if os.path.isfile(pickle_file):
                remove_files.append(f)
                # print('pickle found')
        for f in remove_files:
            try: 
                self.loaded_files.remove(f)
                self.completed_files.append(f)
            except ValueError as e:
                warnings.warn(e)
        self.file_queue.update(self.loaded_files)
        self.completed_queue.update(self.completed_files)

    def fileFinderOSWalk(self, input_dir, fileTypes, *args):
        directoryDepth = 0
        maximum_recursion = 8
        foundFiles = []

        for directoryName, subDirectoryName, fileList in os.walk(input_dir):
            if directoryDepth == 0:
                directoryDepth = len(directoryName.split(os.sep))
            if len(directoryName.split(os.sep)) - directoryDepth >= maximum_recursion:
                warnings.warn('os.walk recursion break triggered')
                break
            
            for item in fileList:
                if item.endswith(fileTypes):
                    fileToAdd = os.path.join(directoryName, item)
                    foundFiles.append(fileToAdd)
        return foundFiles 

    def output_dir(self, outputStyle, styleAttr):
        self.log('output_dir: {}:{}'.format(outputStyle, styleAttr))
        if outputStyle == 'root':
            return self.get_root_output_dir(styleAttr)

    def get_root_output_dir(self, depth):
        self.log('root output: {} depth'.format(depth))
        if depth > 0:
            self.log('solve depth')
            print('''

                variable depth file output
                {}***NOT IMPLEMENTED***{}


                '''.format(color.BOLD, color.END))
        else: 
            if len(self.input_dir) == 1:
                # self.log('input dir: \n{}'.format(self.input_dir))
                output_dir = '{}_Grade_Docs'.format(self.input_dir[0])
            else:
                possible_output = []
                for d in self.input_dir:
                    if d in self.active_file:
                        possible_output.append(d)

                output_dir = '{}_Grade_Docs'.format(max(possible_output, key = len))
            
            os.makedirs(output_dir, exist_ok = True)
            return output_dir

    def log(self, message, prefix = 'File Manager: '):
        if self.development:
            print('{}{}'.format(prefix, message))

class color:
    #http://stackoverflow.com/a/17303428/5079170#
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class ListBoxWithScroll(Frame):
    def __init__(self, master = None):
        self.development = False
        self.log('create listbox with scroll')
        Frame.__init__(self, master)
        self.pack(side = 'top', fill = 'both', expand = 1)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side = 'right', fill ='y')

        self.listbox = Listbox(self, yscrollcommand = scrollbar.set, 
                            selectmode = 'extended',
                            height = 10)
        
        self.listbox.pack(side = 'left', fill = 'both', expand = 1)
        scrollbar.config(command = self.listbox.yview)

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    def update(self, new_list_of_items):
        self.log('empty list, populate with new list')
        self.listbox.delete(0, 'end')
        self.populate(new_list_of_items)

    def populate(self, list_of_items):
        self.log('populate list')
        for item in list_of_items:
            self.listbox.insert('end', item.split(os.sep)[-1])

    @property
    def selection(self):
        self._selection = list(map(int, self.listbox.curselection()))
        return self._selection
    
    def log(self, message, prefix = 'listbox with scroll: '):
        if self.development:
            print('{}{}'.format(prefix, message))

class Application(Frame):

    def __init__(self, input_paths, master = None):
        version = 'Beta 0.8'
        self.development = False
        self.state = 1
        self.master = master
        self.loaded_by_pickle = False
        # self.style = Style()
        if input_paths[0].endswith('.xml'):
            xml_path = input_paths[0]

        elif input_paths[0].endswith('.mgs'):
            self.loaded_by_pickle = True
            self.pickle_data = self.load_pickle(input_paths[0])
            pickle_path = input_paths[0]
        else:
            warnings.warn('File type not recognized')
            raise TypeError('Incorrect file type. Error Code: ID:10T')

        self.paths_to_load = []
        if not self.loaded_by_pickle:
            if len(input_paths) > 1:
                self.paths_to_load = input_paths[1]

        self.log('Starting Application')
        Frame.__init__(self, master)
        master.title('Momisimo Grading System {}'.format(version))
        self.pack(side = 'top', fill = 'both', expand = 0, anchor = 'n')
        master.geometry("700x750")

        if not self.loaded_by_pickle:
            self.manage_xml(xml_path)
        else: 
            self.xml_from_pickle(self.pickle_data)

        self.log('finished managing')

        self.top_frame = Frame(self)
        self.active_file = StringVar()
        self.active_file.set('No active file.')
        self.active_file_label = Label(self.top_frame, text = self.active_file.get(), relief = 'ridge')
        self.active_file_label.pack(side = 'left', fill = 'x', expand = 1)
        self.active_file_label.config(width = 10)
        self.button_label = StringVar()
        self.button_label.set('Load')
        self.button = Button(self.top_frame, text = self.button_label.get(), command = self.load_start)
        self.button.config(width = 5)
        self.button.pack(side = 'right')

        self.top_frame.pack(side = 'top', fill = 'x')

        self.notebook = Notebook(self)

        self.file_manager = FileManager(self.xml_dict['defaults'].find('files_type').text, master = self.notebook)
        
        self.log('Do mains')
        self.mains = []
        for main in self.xml_dict['mains']:
            self.log('main')
            self.mains.append(Maincat(main, self.xml_dict['defaults'], master = self.notebook))
        for main in self.mains:
            self.notebook.add(main, text = main.title)
        self.notebook.add(self.file_manager, text = 'File Info')

        self.notebook.pack(side = 'right', fill = 'both', expand = 1)

        self.gradeInts = GradeIntFields(self.mains, 
                        self.xml_dict['grade_box'],
                        self.xml_dict['defaults'].find('gradeEquation').text, self.grade_total_updater, self)
        for main in self.mains:
            main.gradeInt_updater = self.gradeInts.update_grade_int
            main.gradeTotal_updater = self.grade_total_updater

        self.main_menu = Menu(master)

        self.file_menu = Menu(self.main_menu, tearoff = 0)
        self.file_menu.add_command(label = 'Load Files', command = self.file_manager.load)
        # self.file_menu.add_command(label = 'Load Pickle', command = self.file_manager.load_pickle)
        self.file_menu.add_separator()
        self.file_menu.add_command(label = 'exit', command = master.quit)

        self.main_menu.add_cascade(label = "File", menu = self.file_menu)

        self.sort_menu = Menu(self.main_menu, tearoff = 0)
        self.sort_menu.add_command(label = 'Skip Current', command = self.skip_active)
        self.sort_menu.add_separator()
        self.sort_menu.add_command(label = 'Grade Now', command = self.grade_now)
        self.sort_menu.add_command(label = 'Send to Next', command = self.send_to_next)
        self.sort_menu.add_command(label = 'Send to Last', command = self.send_to_last)
        self.sort_menu.add_command(label = 'Mark as Complete', command = self.mark_as_complete)
        self.sort_menu.add_command(label = 'Move to Queue', command = self.add_to_queue)
        self.sort_menu.add_separator()
        self.sort_menu.add_command(label = 'Remove', command = self.remove_file)
        self.sort_menu.add_separator()
        self.sort_menu.add_command(label = 'Sort Alphabetical', command = self.sort_alphabetical)
        self.sort_menu.add_command(label = 'Sort Modified', command = self.sort_modified_date)
        self.sort_menu.add_command(label = 'Sort Reversed', command = self.sort_reversed)
        self.sort_menu.add_separator()
        self.sort_menu.add_command(label = 'Pickle Filter', command = self.pickle_filter)

        self.main_menu.add_cascade(label = 'Sorting', menu = self.sort_menu)

        master.config(menu = self.main_menu)

        self.pack(side = 'top', fill = 'both', expand = 1)

        self.toggle_state()

        if self.paths_to_load != []:
            self.load_start(self.paths_to_load)

        if self.loaded_by_pickle:
            self.load_file_from_pickle(pickle_path)
            self.button_label.set('Start')
            self.button.config(text = self.button_label.get(), command = self.start)
            self.start()
            self.load_pickle_data()
            #start tool

        # print( 'auto pickle')
        auto_pickle_filter_element = self.xml_dict['defaults'].find('auto_pickle_filter')
        # print('elem: {}'.format(auto_pickle_filter_element))
        # auto_pickle_filter = False
        if auto_pickle_filter_element != None:
            if auto_pickle_filter_element.text.lower() == 'True'.lower():
                self.pickle_filter()
            # print('element found')
            # auto_pickle_filter = auto_pickle_filter_element.text
            # print('filter: {}'.format(auto_pickle_filter))


    def nuke_file(self):
        self.log('Nuke File')
        for main in self.mains:
            #check for incomplete sections, if incomplete set grade to zero...
            main.nuke()
            # raise Exception('finish nuke file method')

    def skip_active(self):
        self.log('skip_active')
        self.file_manager.skip_active()
        self.update_active(self.file_manager.active_file)
        self.reset()

    def grade_now(self):
        self.log('grade_now')
        self.file_manager.grade_now()
        self.update_active(self.file_manager.active_file)

    def send_to_next(self):
        self.log('send_to_next')
        self.file_manager.send_to_next()

    def send_to_last(self):
        self.log('send_to_last')
        self.file_manager.send_to_last()

    def mark_as_complete(self):
        self.log('mark_as_complete')
        self.file_manager.mark_as_complete()

    def add_to_queue(self):
        self.log('add_to_queue')
        self.file_manager.add_to_queue()

    def remove_file(self):
        self.log('remove_file')
        self.file_manager.remove_file()

    def sort_alphabetical(self):
        self.log('sort_alphabetical')
        self.file_manager.sort_alphabetical()

    def sort_modified_date(self):
        self.log('sort_modified_date')
        self.file_manager.sort_modified_date()

    def sort_reversed(self):
        self.log('sort_reversed')
        self.file_manager.sort_reversed()

    def pickle_filter(self):
        self.log('pickle filter')
        self.file_manager.pickle_filter()

    def toggle_state(self):
        if self.state:
            for i in range(len(self.mains)):
                self.notebook.tab(i, state = 'disable')
        else:
            for i in range(len(self.mains)):
                self.notebook.tab(i, state = 'normal')

        self.state = not self.state

    def get_grade(self):
        self.log('get the grade collected')
        main_grades = []
        for main in self.mains: 
            main_grades.append(main.grade)

        grade = {'file' : self.file_manager.active_file,
                 'mains' : main_grades, 
                 'boxes' : self.gradeInts.grade,
                 'total' : self.gradeInts.grade_total_intField[1].get(),
                 'defaults' : self.xml_dict['defaults']}

        return grade 

    def print_grade(self, grade):
        self.log('collected grade is:')
        self.log('{}'.format(grade['file']))
        self.log('====================')
        self.log('====================')
        for main in grade['mains']:
            self.log('{}: {}'.format(main['title'], main['weight']))
            self.log('Highnotes: {}'.format(main['highnotes']))
            self.log('***subs***')
            for sub in main['subs']:
                self.log('\n')
                self.log('{}: {}'.format(sub['title'], sub['weight']))
                self.log('Grade: {}'.format(sub['grade']))
                self.log('Comments: \n{}'.format(sub['user_comments']))
                self.log('Default Comments: \n{}'.format(sub['defaults_comments']))
                self.log('\n')
        self.log('====================')
        for box in grade['boxes']:
            self.log('{} {}'.format(box[2], box[1]))
        self.log('\n')
        self.log('====================')
        self.log('Grade Total: {}'.format(grade['total']))

    def load_start(self, *args):
        self.log('load and swap labels')

        if args:
            self.file_manager.load(args[0])
        else:
            self.file_manager.load()
        self.button_label.set('Start')
        self.button.config(text = self.button_label.get(), command = self.start)

    def start(self):
        if self.file_manager.active_file == '':

            if self.file_manager.loaded_files == []:
                tkinter.messagebox.showerror('No files loaded', 'Please load files to continue')
                raise Exception('No files loaded')

            self.log('Start Grading')
            self.button_label.set('Next')

            # if not self.loaded_by_pickle:
            #     self.button_label.set('Next')
            # else:
            #     self.button_label.set('Done')
            self.reset()
            self.file_manager.cycle_file()

            self.log('next file: {}'.format(self.file_manager.active_file))

            self.update_active(self.file_manager.active_file)

            self.button.config(text = self.button_label.get())
            # self.button.config(command = self.next_file)
            self.toggle_state()
            self.notebook.select(0)
        else:
            self.log('next file')
            self.check_complete()

            #handle text doc output
            d = self.file_output() #output directory
            f = self.build_gradedoc_string(self.get_grade()) #Text String list for output
            self.write_txt_file(d,f)
            
            #handle mgs doc output
            d_mgs = self.mgs_output() #mgs output directory
            #collect grades
            grades_for_pickle = self.gather_grades_for_pickle()
            #build pickle
            # self.write_mgs_file(d_mgs, copy.copy(grades_for_pickle ))
            self.write_mgs_file(d_mgs, grades_for_pickle )

            self.reset()
            # self.toggle_state()
            self.file_manager.cycle_file()
            self.end_of_queue()
            self.update_active(self.file_manager.active_file)
            # self.toggle_state()
            self.notebook.select(0)

    def write_txt_file(self, output_path, output_text_list):
        self.log('write_txt_file')
        # self.log('output path: \n{}'.format(output_path))
        if self.development:
            for line in output_text_list:
                self.log('{}'.format(line))
        filename = '{}.txt'.format(os.path.splitext(self.active_file.get().split(os.sep)[-1])[0]) 
        output_file = self.validate_filename_func(os.path.join(output_path, filename))
        self.log('output file: \n{}'.format(output_file))
        with open(output_file, 'w') as f: 
            for line in output_text_list:
                # f.write('{}{}'.format(line.replace('\n', '<br>\n'), '<br>\n'))
                f.write('{}{}'.format(line, '\n'))

    def write_mgs_file(self, output_path_withFilename, grades):
        self.log('write mgs files')
        filename = '{}.mgs'.format(output_path_withFilename)
        output_file = self.validate_filename_func(filename)
        self.log('mgs output: {}'.format(output_file))

        built_for_pickle = (self.xml_dict, grades)
        pickle_to_write = pickle.dumps(built_for_pickle)
        with open(output_file, 'wb') as f:
            f.write(pickle_to_write)
            f.close() 
        # print('mgs written successfully!')

    def __getstate__(self):
        # http://stackoverflow.com/a/5972505/5079170
        state = self.__dict__.copy()
        if 'view' in state:
            del state['view']
        return state

    def gather_grades_for_pickle(self):
        self.log('gather grades for pickle')

        grades = []
        #collect main cat grades
        for cat in self.mains:
            self.log('collecting: {}'.format(cat.title))

            grades.append(cat.grade)

        #collect grade box grades
        grade_int_box = self.gradeInts.grade
        grades.append(grade_int_box)

        return grades 

    def validate_filename_func(self, input_filename_w_path):
        if os.path.isfile(input_filename_w_path):
            if tkinter.messagebox.askokcancel('File Exists.', 'Press "OK" to Iterate "Cancel" to Overwrite.'):
                #Iterate the file
                if os.path.isfile(input_filename_w_path):
                    the_file = input_filename_w_path
                    i = 1
                    while os.path.isfile(the_file):
                        splitext = list(os.path.splitext(the_file))
                        if i > 1:
                            splitext[0] = splitext[0].rsplit('_', 1)[0]
                        the_file = '{}_{:02d}{}'.format(splitext[0], i, splitext[1])
                        i += 1
                        if i > 10:
                            raise Exception('Filename not validated: {}: {}'.format(the_file, i))
                    return the_file 
            else:
                #Overwrite the file
                if os.path.isfile(input_filename_w_path):
                    os.remove(input_filename_w_path)
                return input_filename_w_path
        else:
            return input_filename_w_path

    def mgs_output(self):
        self.log('mgs output')
        mgs_fileDir = os.path.splitext(self.file_manager.active_file)[0]
        # print('mgs: {}'.format(mgs_fileDir))

        return mgs_fileDir

    def file_output(self):
        self.log('file output')
        output = self.xml_dict['defaults'].find('output')
        output_style = output.text

        if output_style == 'root':
            output_attr = int(output.get('depth'))

            self.log('output: {}'.format(output_style))
            self.log('depth: {}'.format(output_attr))

        output_dir = self.file_manager.output_dir(output_style, output_attr)
        self.log('Grade Docs: \n{}'.format(output_dir))
        return output_dir

    def build_gradedoc_string(self, grade):
        self.log('build grade doc string')
        width = 50
        line_separator = ['-' * width,]
        newline = ' '
        xmlDefaults = self.xml_dict['defaults']

        def wordwrap(inputText, wrapWidth = width):
            return textwrap.wrap(inputText, wrapWidth)

        fileout = []
        fileout.extend(wordwrap('Grading for: {}'.format(self.active_file.get().split(os.sep)[-1])))
        fileout.extend(line_separator)
        fileout.extend(newline)

        #grade total text
        total_intro_text = None
        if xmlDefaults.find('total_intro') != None:
            total_intro_text = xmlDefaults.find('total_intro').text
        if total_intro_text == None:
            total_intro_text = ''
        fileout.extend(wordwrap('{}{}%'.format(total_intro_text, grade['total'])))
        fileout.extend(line_separator)
        fileout.extend(newline)

        #iterate main sections
        for main in grade['mains']:
            #Main category title and grade value
            fileout.extend(wordwrap('{}: {}%'.format(main['title'], main['grade'])))
            fileout.extend(line_separator)
            fileout.extend(newline)

            #if highnotes, add to output
            if main['highnotes'] != '':
                highnotes_intro = None
                if xmlDefaults.find('highnote_intro') != None:
                    highnotes_intro = xmlDefaults.find('highnote_intro').text
                if highnotes_intro == None:
                    highnotes_intro = ''
                fileout.extend(wordwrap('{}{}'.format(highnotes_intro, main['highnotes'])))
                fileout.extend(line_separator)
                fileout.extend(newline)

            #iterate subsections
            for sub in main['subs']:
                #sub category title and grade value
                if xmlDefaults.find('print_subgrades') != None:
                    if xmlDefaults.find('print_subgrades').text == 'True':
                        fileout.extend(wordwrap('{}: {}%'.format(sub['title'], sub['grade'])))
                else:
                    fileout.extend(wordwrap('{}'.format(sub['title'])))
                fileout.extend(line_separator)
                fileout.extend(newline)

                #default comments
                if sub['defaults_comments'] != None or sub['defaults_comments'] != '':
                    if xmlDefaults.find('default_comment_intro') != None: 
                        default_comment_intro = xmlDefaults.find('default_comment_intro').text
                        if default_comment_intro == None:
                            default_comment_intro = ''
                        fileout.extend(wordwrap('{}{}'.format(default_comment_intro, 
                                                                sub['defaults_comments'])))
                    else: 
                        fileout.extend(wordwrap('{}'.format(sub['defaults_comments'])))
                    fileout.extend(newline)

                #user comments
                if sub['user_comments'] != None or sub['user_comments'] != '':
                    if xmlDefaults.find('comment_intro') != None: 
                        user_comment_intro = xmlDefaults.find('comment_intro').text
                        if user_comment_intro == None:
                            user_comment_intro = ''
                        fileout.extend(wordwrap('{}{}'.format(user_comment_intro, 
                                                                sub['user_comments'])))
                    else: 
                        fileout.extend(wordwrap('{}'.format(sub['user_comments'])))
                    fileout.extend(newline)

                fileout.extend(line_separator)
                fileout.extend(newline)

        #collection of all main grades
        for main in grade['mains']:
            fileout.extend(wordwrap('{}: {}%'.format(main['title'], main['grade'])))

        fileout.extend(newline)

        #iterate through grade boxes
        for box in grade['boxes']:
            fileout.extend(['{}{}'.format(box[2], box[1]),])

        fileout.extend(line_separator)
        fileout.extend(newline)

        #grade total text
        total_intro_text = None
        if xmlDefaults.find('total_intro') != None:
            total_intro_text = xmlDefaults.find('total_intro').text
        if total_intro_text == None:
            total_intro_text = ''
        fileout.extend(wordwrap('{}{}%'.format(total_intro_text, grade['total'])))

        # fileout.extend(['<!-- {}: {}-->'.format(grade['total'], self.active_file.get().split(os.sep)[-1][:20])])
        fileout.extend(['\n\n{}: {}%'.format(self.active_file.get().split(os.sep)[-1][:20], grade['total'])])

        return fileout

    def end_of_queue(self):
        self.log('test for end of queue')
        if self.loaded_by_pickle:
            x = tkinter.messagebox.showinfo('File Complete', 'Grading update completed.')
            self.master.quit()
        else: 
            if self.file_manager.active_file == 'end of queue':
                eoq_message = 'Grade queue completed.\nSelect OK to quit. Cancel to load.'
                if tkinter.messagebox.askokcancel('End of Queue', eoq_message):
                    self.log('EOQ confirmed. - QUIT')
                    self.master.quit()
                else:
                    self.log('EOQ - Load')
                    self.toggle_state()
                    self.file_manager.load()
                    self.button_label.set('Start')
                    self.button.config(text = self.button_label.get(), command = self.start)
                    self.reset()
                    self.active_file.set('')
                    self.file_manager.active_file = ''

    def reset(self):
        self.log('reset')
        self.gradeInts.reset()
        for main in self.mains:
            main.reset()

    def check_complete(self):
        self.log('check tool for completeness')

        incomplete_list = []

        for main in self.mains:
            self.log('isComplete: {}'.format(main.title))
            temp = main.isComplete()
            self.log('{}'.format(temp))
            if temp != []:
                incomplete_list.append(temp)

        if incomplete_list != []:
            error_message = ''
            error_message += '\n\nGrading not complete.\nPlease complete grade tool to cycle the file.\n'
            error_message += '===========================\n'
            # error_message += '===========================\n'
            for main in incomplete_list:
                error_message += '\nCategory: {}\n'.format(main[0])
                error_message += '---------------------------\n'
                for sub in main[1]:
                    error_message += '{}\n'.format(sub)
                # error_message += '---------------------------\n'
                # error_message += '---------------------------\n'
            error_message += "\nOk to fix. Canel to Nuke>Zero incomplete fields."
            box_results = tkinter.messagebox.askokcancel('Grade Tool Incomplete', error_message)
            if box_results != True:
                self.nuke_file()
            else:
                raise Exception('Grade tool not complete.')

            # tkinter.messagebox.showerror('Grade Tool Incomplete', error_message)
            # raise Exception('Grade tool not complete.')

    def update_active(self, new_file):
        self.active_file.set(new_file)
        self.active_file_label.config(text = self.active_file.get().split(os.sep)[-1])
        self.log('active file: \n{}'.format(new_file))

    def grade_total_updater(self, *args):
        self.log('update grade total')
        title_weight_tuples = []
        for main in self.mains:
            title_weight_tuples.append((main.title, main.weight))
        self.gradeInts.update_grade_total(title_weight_tuples)
            
    def manage_xml(self, xml_path):
        self.log('Parse xml')
        self.log('FilePath: {}'.format(xml_path))
        xml_elementTree = etree.ElementTree(file = xml_path)
        xml_root = xml_elementTree.getroot()

        self.xml_dict = {'defaults': xml_root.find('defaults'),
                        'mains': xml_root.findall('category'),
                        'grade_box': xml_root.findall('grade_box')}

        self.validate_xml()

    def validate_xml(self):
        self.log('Validate XML')
        error_list = []
        cat_weights = 0
        eq = self.xml_dict['defaults'].find('gradeEquation').text
        self.log('equation: {}'.format(eq))

        cats_to_validate = 0
        for cat in self.xml_dict['mains']:

            cat_title = cat.get('title')
            if cat_title == None:
                cat_title = cat.find('title').text

            cat_weight = cat.get('weight')
            if cat_weight == None:
                cat_weight = cat.find('weight').text

            if eq.count(cat_title[:3]) != 1:
                self.log('title: {}'.format(cat_title[:3]))
                self.log('count: {}'.format(eq.count(cat_title[:3])))
                error_list.append('{} \nnot present in equation exactly once.'.format(cat_title))


            ignore_validation = cat.find('ignore_validation')
            if ignore_validation != None:
                if ignore_validation.text.lower() == 'true':
                    ignore_validation = True
            else:
                ignore_validation = False


            if not ignore_validation:
                cat_weights += float(cat_weight)
                cats_to_validate += 1
            else:
                print('Category: {} ignored in validation.'.format(cat_title))


            subcat_weights = 0
            subs_to_validate = 0
            for subcat in cat.findall('subcategory'):

                sub_title = subcat.get('title')
                if sub_title == None:
                    sub_title = subcat.find('title').text

                sub_weight = subcat.get('weight')
                if sub_weight == None:
                    sub_weight = subcat.find('weight').text

                ignore_validation = subcat.find('ignore_validation')
                if ignore_validation != None:
                    if ignore_validation.text.lower() == 'true':
                        ignore_validation = True
                else:
                    ignore_validation = False

                if not ignore_validation:
                    subcat_weights += float(sub_weight)
                    subs_to_validate += 1
                else:
                    print('Subcategory: {} ignored in validation.'.format(sub_title))

            self.log('total subcat weighting: {}'.format(subcat_weights))

            if (subcat_weights != 100) and (subs_to_validate != 0):
                error_list.append('{} \nsubweights incorrect. Total weights: {}'.format(cat_title, subcat_weights))
                warnings.warn('Subcategory weighting incorrect!\n{} total subcategory weighting: {}'.format(
                    cat_title, subcat_weights))
                error_list.append('\n')

        for box in self.xml_dict['grade_box']:
            self.log('box: {}'.format(box.get('title')))
            if box.get('title') == 'Late':
                if eq.count(box.get('title')) != 1:
                    error_list.append('{} Grade Box\nnot present in equation exactly once'.format(box.get('title')))
            elif eq.count(box.get('title')[:3]) != 1:
                error_list.append('{} Grade Box\nnot present in equation exactly once'.format(box.get('title')))

        self.log('total cat weighting: {}'.format(cat_weights))
        if (cat_weights != 100) and (cats_to_validate != 0): 
            error_list.append('\nCategory weights incorrect. Total weights: {}'.format(cat_weights))
            warnings.warn('Category Weighting Incorrect!\nTotal category weight: {}'.format(cat_weights))

        if len(error_list) >= 1:
            self.log('len(error_list): {}'.format(len(error_list)))
            self.log('error_list: {}'.format(error_list))
            msg = ''
            for i in error_list:
                msg += '{}\n'.format(i)

            prelist = ['Oh Snap!', 'Stop the ship!', 'Well butter my biscuits!',
                        'I better fix that!', 'Oopsie daisy!', "Yup, that's about right"]
            button_list = random.sample(prelist, 2)
            button_list.append('Continue Anyway')
            random.shuffle(button_list)

            if msg != '':
                # print('\nXML Validation Error!\n{}\n\n'.format(msg))
                raise Exception('\nXML Validation Error!\n{}\n\n'.format(msg))

    def load_pickle(self, path_to_pickle):
        self.log('load pickle data from file')
        with open(path_to_pickle, 'rb') as pickle_file:
            pickle_data = pickle.loads(pickle_file.read())
        return pickle_data

    def xml_from_pickle(self, pickle_data):
        self.log('xml from pickle')
        self.xml_dict = pickle_data[0]

    def load_file_from_pickle(self, pickle_path):
        self.log('find pickle file')
        self.file_manager.load_file_from_pickle(pickle_path)

    def load_pickle_data(self):
        self.log('load pickle data')
        grade_data = self.pickle_data[1]

        grade_boxes = self.gradeInts.grade
        for g in grade_data:
            if isinstance(g, dict): 
                for cat in self.mains:
                    if g['title'] == cat.title:
                        cat.grade = g 
            else:
                loaded_boxes = g
        for loaded_box in loaded_boxes:
            for box in grade_boxes:
                if loaded_box[3]['title'] == box[3]['title']:
                    self.gradeInts.grade = loaded_box[3]

    def log(self, message, prefix = 'App: '):
        if self.development:
            print('{}{}'.format(prefix, message))

#######
#######
#######
#######

print('Starting Momisimo Beta 0.10') #Version

#######
#######
#######
#######

def print_usage():
    print('''
    Momisimo Usage:
    In the terminal type: python3<space>
    Drag the Momisimo script file into the terminal
    Drag the grading document xml file into the terminal
     -Instead of a grading document xml you can use 
      .mgs pickle files to reload a graded file. 
    Press <enter>
    The tool will then build and launch


    Optionally you can drag the file directories into the terminal after the xml. 
    This will 'auto load' files based on format specified in xml. 
    ''')

def validate_input(sys_args):
    input_arg = sys_args
    # print('input_arg: {}'.format(input_arg))
    # print('len: {}'.format(len(input_arg)))
    return_files = []
    if len(input_arg) == 1:
        print_usage()
        sys.exit()
    
    if len(input_arg) == 2:
        if not input_arg[1].endswith(('.xml', '.mgs')):
            raise ValueError('Incorrect input format. File must be of extension ".xml" or ".mgs".')
        if not os.path.isfile(input_arg[1]):
            raise ValueError('Incorrect input. Input must be a file')
        return_files.append(input_arg[1])

    if len(input_arg) > 2:
        return_files = []

        if not input_arg[1].endswith(('.xml', '.mgs')):
            raise ValueError('Incorrect input format. File must be of extension ".xml" or ".mgs".')
        if not os.path.isfile(input_arg[1]):
            raise ValueError('Incorrect input. Input must be a file')
        return_files.append(input_arg[1])

        file_dirs = []
        for d in input_arg[2:]:
            if not os.path.isdir(d):
                warnings.warn('Included paths must lead to folders.')
                warnings.warn('Path is not a folder. \n{}'.format(d))
            else:
                file_dirs.append(d)
        if file_dirs != []:
            return_files.append(file_dirs)
    return return_files

input_paths = validate_input(sys.argv)

root = Tk()
app = Application(input_paths, master=root)
app.mainloop()