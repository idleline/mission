from flask_nav import Nav
from dominate import tags
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator, NavigationItem
#from flask_nav.elements import NavigationItem
from flask_bootstrap.nav import BootstrapRenderer, sha1
from flask_security import current_user

nav = Nav()

class ExtendedNavbar(NavigationItem):
    ''' Modified Navbar for Bootstrap to display right side menu items '''
    
    def __init__(self, title, root_class='navbar navbar-default', items=[], right_items=[]):
        self.title = title
        self.root_class = root_class
        self.items = items
        self.right_items = right_items
    
class CustomBootstrapRenderer(BootstrapRenderer):
    ''' Custom render for ExtendedNavbar '''
    
    def visit_ExtendedNavbar(self, node):
        # create a navbar id that is somewhat fixed, but do not leak any
        # information about memory contents to the outside
        node_id = self.id or sha1(str(id(node)).encode()).hexdigest()

        root = tags.nav() if self.html5 else tags.div(role='navigation')
        root['class'] = node.root_class

        cont = root.add(tags.div(_class='container-fluid'))

        # collapse button
        header = cont.add(tags.div(_class='navbar-header'))
        btn = header.add(tags.button())
        btn['type'] = 'button'
        btn['class'] = 'navbar-toggle collapsed'
        btn['data-toggle'] = 'collapse'
        btn['data-target'] = '#' + node_id
        btn['aria-expanded'] = 'false'
        btn['aria-controls'] = 'navbar'

        btn.add(tags.span('Toggle navigation', _class='sr-only'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))
        btn.add(tags.span(_class='icon-bar'))

        # title may also have a 'get_url()' method, in which case we render
        # a brand-link
        if node.title is not None:
            if hasattr(node.title, 'get_url'):
                header.add(tags.a(node.title.text, _class='navbar-brand',
                                  href=node.title.get_url()))
            else:
                header.add(tags.span(node.title, _class='navbar-brand'))

        bar = cont.add(tags.div(
            _class='navbar-collapse collapse',
            id=node_id,
        ))
        bar_list = bar.add(tags.ul(_class='nav navbar-nav left'))
        for item in node.items:
            bar_list.add(self.visit(item))

        if node.right_items:
            right_bar_list = bar.add(tags.ul(_class='nav navbar-nav navbar-right'))
            for item in node.right_items:
                right_bar_list.add(self.visit(item))

        return root

def init_custom_nav_renderer(app):
    # For some reason, this didn't seem to do anything...
    #app.extensions['nav_renderers']['bootstrap'] = (__name__, 'CustomBootstrapRenderer')
    # ... but this worked. Weird.
    app.extensions['nav_renderers'][None] = (__name__, 'CustomBootstrapRenderer')

@nav.navigation(id='main_nav')
def main_nav():
    ''' Implements Navbar to build a top navigation menu '''

    navbar = ExtendedNavbar(title = View(' unTrust', 'untrust.index'))

    if current_user.is_authenticated is True:
        username = current_user.username
        navbar.items = [
            View(' Search', 'untrust.search'),
            View(' Dashboard', 'untrust.dashboard'),
            Subgroup(' Tattletale', View(' View', 'tattletale.tableview'),
            View(' Add', 'tattletale.add_tattletale')),
            View(' Wildrice', 'untrust.wildrice'),
            View(u' IP m\u014dl', 'ipmol.index'),
            View(' RiskDNS', 'untrust.pdns')]

        navbar.right_items = [View(' {0}'.format(username), 'admin.profile'), # right_items
            View(' Logout', 'auth.logout')]

        if current_user.has_role('superuser'):
            navbar.right_items.append(View(" Admin", 'admin.admin'))

    else:
        navbar.items = [View(' Search', 'untrust.search')]
        navbar.right_items = [View(' Login', 'auth.login')]
    
    return navbar

nav.register_element('main_nav', main_nav)