'''
    
    mission.lib.assets
    
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
layout_css = Bundle(
    'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/bootstrap-select/1.13.3/css/bootstrap-select.min.css',
    'css/pp-fonts.css',
    'https://use.fontawesome.com/releases/v5.5.0/css/all.css',
    )

datatables_css = Bundle(
    'https://cdn.datatables.net/1.10.18/css/dataTables.bootstrap4.min.css',
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
        'https://code.jquery.com/jquery-3.3.1.min.js',
        'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js',
        'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js',
        'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js'
        'js/home.js'
        )
    
datatable_js = Bundle(
        'https://cdnjs.cloudflare.com/ajax/libs/datatables/1.10.19/js/jquery.dataTables.min.js',
        'https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap4.min.js',
        'js/map_dt.js'
        )

'''
    : Bundles :
    
    Dictionary of assets
'''
bundles = {
    'layout_css'    : layout_css,
    'datatables_css': datatables_css,
    'master_css'    : master_css,
    'layout_js'     : layout_js,
    'datatable_js'  : datatable_js,
}