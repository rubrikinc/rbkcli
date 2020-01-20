from datetime import datetime
import os
import jinja2


g_table = """
    <table align="center" style="{{ style }}">
        <caption style="{{ title_style }}">{{ title }}</caption>
        <font face="'Roboto', Arial, sans-serif">
           {{ lines }}
        </font>
    </table>
"""
g_line = """
        <tr style="{{ style }}">
            {{ a_line }}
        </tr>
"""
g_row = """
            <td style="{{ style }}">{{ a_row }}</td>
"""
g_head_row = """
            <th style="{{ style }}"><font face="'Roboto', Arial, sans-serif">
            {{ a_row }}
            </font></th>
"""
##63adfb
g_main_header = """
    <table align="center" border="0" cellpadding="0" cellspacing="0"
     width="80%">
        <tr>
            <td align="left" bgcolor="#66b1ab" style="padding: 30px 30px 30px
             30px;font-size:30px; color:#FFFFFF;" width="50%">
                <font face="'Roboto', Arial, sans-serif">
                    rbkcli html report
                </font>
                <p style="font-size:15px;text-align:left">
                <b>Source:</b> {{ source }}<br>
                <b>Command:</b> {{ command }}<br>
                <b>Date:</b> {{ rep_time }}
                </p>
            </td>
            <td align="center" bgcolor="#66b1ab" style=" font-size:8px;" width="50%">
                <font style="color: #FFFFFF;" face="'Roboto', Arial, sans-serif">
                    {{ logo_location }}
                </font>
            </td>
        </tr>
    </table>
    <table align="left" border="0" cellpadding="0" cellspacing="0"
     width="100%">
        <tr>
            <td style="font-size: 0; line-height: 0;" height="30">&nbsp;</td>
        </tr>
    </table>

"""
g_page = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" 
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>{{ page_title }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>
    <body style="margin: 0; padding: 0;">
        {{ page_header }}
        {{ page_summary }}
    <table align="left" border="0" cellpadding="0" cellspacing="0"
     width="100%">
        <tr>
            <td style="font-size: 0; line-height: 0;" height="30">&nbsp;</td>
        </tr>
    </table>
    <table align="center" border="0" cellpadding="0" cellspacing="0"
     width="80%">
        <tr>
            <td style="font-size: 28px;" height="30"><b>{{ summary }}</b></td>
        </tr>
    </table>
    <table align="left" border="0" cellpadding="0" cellspacing="0"
     width="100%">
        <tr>
            <td style="font-size: 0; line-height: 0;" height="30">&nbsp;</td>
        </tr>
    </table>
    </body>
</html>
"""
logo_line = """

"""
asc_logo = """
                `-`                
         -+o  `/sss/`  ++-         
         `-+`/sssssso/`/-`         
      -oo++/.+sssssso+./++++-      
  `:` :sssso  .+oso+.  ooooo: `-`  
  /++-:++++/    .:.    /++++:-/+:  
    .+o/`                 `:+/.    
  -+sssso/.             `:ooooo/.  
 :sssssssso.           .+oooooooo: 
  -+sssso/`             `:ooooo/.  
    .+o:`                 `:+/.    
  /+/-:++++/    .:.    /////:.//:  
  `:` :ooooo  ./ooo/.  +oooo: `-`  
      -++++/./ooooooo/./++++-      
         `-/`/ooooooo/`/-          
         -++  `:ooo/`  ++-         
                `-`                
"""

class Tabelfier:
    def __init__(self, command, title, header, columns, summary):
        self.command = command
        self.summary = summary
        self.title = title
        self.header = header
        self.columns = columns
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
        )

    def gen_head_row(self, row, line):
        # row_template = self.jinja_env.get_template("head_row.html")
        row_template = self.jinja_env.from_string(g_head_row)
        rendered_row = row_template.render(a_row=row,
                                           style='background-color: #63adfb; '
                                                 'font-size:24px; padding: '
                                                 '15px;', )
        line.append(rendered_row)
        return line

    def gen_row(self, row, line, ix=0):
        # row_template = self.jinja_env.get_template("row.html")
        row_template = self.jinja_env.from_string(g_row)
        rendered_row = row_template.render(a_row=row,
                                           style='border: 1px solid #eee; '
                                                 'border-collapse: collapse; '
                                                 'padding: 15px;')
        line.append(rendered_row)
        return line

    def gen_line(self, line, table, ix=0):
        # line_template = self.jinja_env.get_template("line.html")
        line_template = self.jinja_env.from_string(g_line)
        style = 'background-color: #eee;'
        if ix % 2 == 0:
            style = 'background-color: #fff;'

        rendered_line = line_template.render(a_line='\n'.join(line),
                                             style=style)
        table.append(rendered_line)
        return table

    def gen_table(self, table_lines):
        # table_template = self.jinja_env.get_template("table.html")
        table_template = self.jinja_env.from_string(g_table)
        style = 'width:80%; border: 0; border-collapse: collapse; ' \
                'border-spacing: 5px;'
        table = table_template.render(title_style='font-size:32px;',
                                      style=style,
                                      lines='\n'.join(table_lines))
        return table

    def iterate(self):
        my_lines = []
        for i in range(0, len(self.columns[0])):
            my_rows = []
            if i == 0:
                for head in self.header:
                    my_rows = self.gen_head_row(head, my_rows)
                my_lines = self.gen_line(my_rows, my_lines, ix=i)
                my_rows = []

            for row in self.columns:
                my_rows = self.gen_row(row[i], my_rows)

            my_lines = self.gen_line(my_rows, my_lines, ix=i)

        self.my_table = self.gen_table(my_lines)

    def assemble(self):
        self.iterate()
        logo = self.add_logo()
        header_template = self.jinja_env.from_string(g_main_header)
        headeri = header_template.render(source='rbkcli',
                                         command=self.command,
                                         rep_time=str(datetime.now()),
                                         logo_location=logo)
        # template = self.jinja_env.get_template("table_template.html")
        template = self.jinja_env.from_string(g_page)
        rendered = template.render(page_title=self.title,
                                   page_header=headeri,
                                   page_summary=self.my_table,
                                   summary=self.summary)

        return rendered

    def add_logo(self):
        lines = self.jinja_env.from_string(g_line)
        asc_logo_1 = asc_logo
        asc_logo_1 = asc_logo_1.split('\n')
    
        rendered_line = ''
        for line in asc_logo_1:
            rendered_line += '                    <b>%s</b><br>\n' % line.replace(" ", "&nbsp;&nbsp;")

        return rendered_line

    def export(self):

        html_table = self.assemble()

        with open('table_test.html', 'w') as test:
            test.write(html_table)
