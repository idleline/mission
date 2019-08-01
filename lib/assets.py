'''
    
    dmarc.lib.assets
    
    Defines the flask bundles for combining and minifying
    client side assets
'''

from flask_assets import Bundle

'''
    : Stylesheet Bundles : 
    
    {layout_css}        Used in layout.html for global CSS
    {datatables_css}    Used in datatables
    {master_css}        Last loaded CSS for overrides
'''
theme_scss = Bundle(
    'css/theme.scss',
    filters = 'pyscss',
    output = 'css/_theme.scss'
    )

layout_css = Bundle(
    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.3/css/bootstrap-select.min.css',
    'css/pp-fonts.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css',
    'https://pro.fontawesome.com/releases/v5.9.0/css/all.css',
    'https://cdnjs.cloudflare.com/ajax/libs/hover.css/2.3.1/css/hover-min.css',
    'css/app.css',
    )

datatables_css = Bundle(
    'https://cdn.datatables.net/1.10.19/css/dataTables.bootstrap4.min.css',
    'https://cdn.datatables.net/select/1.3.0/css/select.bootstrap4.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.5/css/select2.css',
    )
    
master_css = Bundle(
    'css/style.css'
    )

'''
    : Javascript Bundles : 
    
    {layout_js}     Used in layout.html for global JS
    {datatable_js}  Used in index.html for loading datatable functions
''' 
layout_js = Bundle(
        'https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js',
        'https://code.jquery.com/jquery-2.2.4.min.js',
        'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.22.2/moment.min.js',
        'https://unpkg.com/popper.js@1.14.6/dist/umd/popper.min.js',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js',
        'js/detect.js',
        'https://cdnjs.cloudflare.com/ajax/libs/fastclick/1.0.6/fastclick.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/jquery.blockUI/2.70/jquery.blockUI.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/jquery.nicescroll/3.7.6/jquery.nicescroll.min.js',
        'https://cdn.jsdelivr.net/npm/parsleyjs@2.8.1/dist/parsley.min.js',
        output='js/layout.js',
        )
    
datatables_js = Bundle(
        'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.4.0/Chart.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/js/jquery.dataTables.min.js',
        'https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap4.min.js',
        'https://cdn.datatables.net/select/1.3.0/js/dataTables.select.min.js',
        'https://cdn.datatables.net/select/1.3.0/js/select.jqueryui.min.js',
        'https://cdn.datatables.net/select/1.3.0/js/select.bootstrap4.min.js',
        )

counterup_js = Bundle(
        'js/jquery.waypoints.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/Counter-Up/1.0.0/jquery.counterup.min.js',
        )
        
dmarc_js = Bundle(
        'js/dmarc.js'
        )

dashboard_js = Bundle(
        'js/dashboard.js'
        )
    
charts_js = Bundle(
        'js/charts.js'
)

'''
    : Bundles :
    
    Dictionary of assets
'''
bundles = {
    'theme_scss'    : theme_scss,
    'layout_css'    : layout_css,
    'datatables_css': datatables_css,
    'master_css'    : master_css,
    'layout_js'     : layout_js,
    'datatables_js' : datatables_js,
    'counterup_js'  : counterup_js,
    'dmarc_js'      : dmarc_js,
    'charts_js'     : charts_js,
    'dashboard_js'  : dashboard_js,
}

scss_bundles = {
    'theme_scss'    : theme_scss
}