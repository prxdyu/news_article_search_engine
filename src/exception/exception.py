# importing the required libraries
import sys

# creating a custom exception class
class CustomException(Exception):

    def __init__(self,error_msg,error_details:sys):
        
        self.error_msg = error_msg
        # getting the details of the error
        _,_,exc_tb = error_details.exc_info()
        # getting the line no from where error occurs
        self.line_no=exc_tb.tb_lineno
        # getting the filename from where error occurs
        self.file_name=exc_tb.tb_frame.f_code.co_filename


    def __str__(self):
        return f"Error occured in the python script [ {self.file_name} ] at the line {self.line_no} Error message: {str(self.error_msg)}"


if __name__=="__main__":

    try:
        a=1/0

    except Exception as e:
        raise CustomException(e,sys)