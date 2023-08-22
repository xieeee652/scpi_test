import pyvisa
import time
import numpy
import errno

TIMEOUT = 3000 #3sec


class SCPI:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()


    def search(self):
        table = []
        try:
            resources = self.rm.list_resources()
            for selection in resources:
                try:
                    with self.rm.open_resource(selection) as inst:
                        idn = inst.query('*IDN?')
                        table.append((selection, idn))
                except pyvisa.Error as e:
                    table.append((selection, f"Error: {e}"))
        except pyvisa.errors.VisaIOError as e:
            return self._handle_visa_error(e)
    
        return table

    # def search(self):
    #     table = self.rm.list_resources()
    #     for selection in table:
    #         with self.rm.open_resource(selection) as inst:
    #             print(f"{inst.resource_name},{inst.query('*IDN?')}")

    # normal query & write
    def execute(self, device, instruction, is_query=False):
        with self.rm.open_resource(device) as inst:
            try:
                inst.timeout = TIMEOUT 
                if is_query:
                    data = inst.query(instruction)
                    return data
                    # print("成功讀取數據:", data)
                else:
                    inst.write(instruction)
                    # print("指令寫入成功")
                    return pyvisa.constants.VI_SUCCESS
            except pyvisa.errors.VisaIOError as e:
                return self._handle_visa_error(e)
    

    def query_full_response(self, device, instruction, delay=1):
        with self.rm.open_resource(device) as inst:
            try:
                inst.timeout = TIMEOUT
                inst.write(instruction)

                full_response = ""

                while True:
                    response_part = inst.read()
                    full_response += response_part

                    # 判斷是否已經接收到完整的回應
                    if self._is_full_response_received(full_response):
                        break

                    time.sleep(delay)

                # print("完整回應:", full_response)
            except pyvisa.errors.VisaIOError as e:
                return self._handle_visa_error(e)

            return full_response


    def _is_full_response_received(self, full_response, termination=''):
        return full_response.endswith(termination)

    # def query_ascii(self, device, instruction, values, is_query=False):
    #     with self.rm.open_resource(device) as inst:
    #         try:
    #             if is_query:
    #                 values = inst.query_ascii_values(instruction, container=numpy.array)
    #                 # 打印解析後的數值列表
    #                 print("解析後的數值列表:", values)
    #             else:
    #                 inst.write_ascii_values(instruction, values)
    #                 print("指令寫入成功")
    #         except pyvisa.errors.VisaIOError as e:
    #             self._handle_visa_error(e)

    def _handle_visa_error(self, error):
        if error.error_code == pyvisa.constants.VI_ERROR_TMO:
            return pyvisa.constants.VI_ERROR_TMO
        elif error.error_code == pyvisa.constants.VI_ERROR_INV_SESSION:
            return pyvisa.constants.VI_ERROR_INV_SESSION
        elif error.error_code == pyvisa.constants.VI_ERROR_RSRC_NFOUND:
            return pyvisa.constants.VI_ERROR_RSRC_NFOUND
        elif error.error_code == pyvisa.constants.VI_ERROR_IO:
            return pyvisa.constants.VI_ERROR_IO
        else:
            print("操作錯誤:", error)
            return error.error_code

    # def _handle_visa_error(self, error):
    #     if error.error_code == pyvisa.constants.VI_ERROR_TMO:
    #         print("操作超時")
    #     else:
    #         print("操作錯誤:", error)


if __name__ == "__main__":
    my_scpi = SCPI()
    a = my_scpi.search()
    device_name = "TCPIP::192.168.0.10::INSTR"
    instruction_to_send = ":SENSe:FREQuency:STOP?"
    print(a)
    ex = my_scpi.execute(device_name, instruction_to_send, is_query=True)
    print(ex)
    full = my_scpi.query_full_response(device_name, instruction_to_send)
    print(full)
    # 或者使用以下命令寫入指令
    # my_scpi.execute(device_name, "SOME_COMMAND")