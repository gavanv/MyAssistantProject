

def function_nir(aa=1, *args, tt=1, **kwargs):
    print("args", *args)
    print(kwargs)
    print("tt", tt)


function_nir(3, 6, 8, 3, 2, tt=6, nir="hie", rtg="234", tgs="345")


# db_connection = ""


# def _structure_with_db_connection(method):

#     def new_function(self, *args, **kwargs):
#         global db_connection

#         try:

#             print("Fetching from db")
#             results = 234

#             method(self,results, *args, **kwargs)

#             print("Finished, here are the results")

#         except Exception as e:
#             print(str(e))
#     return new_function


# @_structure_with_db_connection
# def task1(results):

#     print("using db data to perform some more calculations.." + results)


# @_structure_with_db_connection
# def task2(results):

#     print("using db data to perform some more calculations.. little different then task1" + results)


# def task3():

#     global db_connection

#     try:

#         print("Fetching from db")

#         print("using db data to perform some more calculations.. little different then task1 & task2" + db_connection)

#         print("Finished, here are the results")

#     except Exception as e:
#         print(str(e))
