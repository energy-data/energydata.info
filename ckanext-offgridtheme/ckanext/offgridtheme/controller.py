import ckan.lib.base as base
render = base.render

class ToolsController(base.BaseController):

    def view(self):
        return render('offgridpages/tools.html')

# One controller per page.
# class AnotherController(base.BaseController):

#     def view(self):
#         return render('offgridpages/another.html')
