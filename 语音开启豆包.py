import speech_recognition as sr
import pyautogui
import threading
import time

# 语音识别设置
r = sr.Recognizer()
mic = sr.Microphone()

# 监听状态标志
is_listening = True

def execute_alt_f():
    """执行Alt+F组合键"""
    pyautogui.hotkey('alt', 'f')
    print("已执行 Alt+F")

def recognize_speech():
    """持续监听语音指令"""
    global is_listening
    with mic as source:
        r.adjust_for_ambient_noise(source)  # 适应环境噪音
    
    while is_listening:
        try:
            with mic as source:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            text = r.recognize_google(audio, language='zh-CN')
            print(f"识别到: {text}")
            
            # 检测关键词
            if "菜单" in text or "文件" in text:
                execute_alt_f()
                
        except sr.WaitTimeoutError:
            continue  # 超时继续监听
        except sr.UnknownValueError:
            continue  # 无法识别继续监听
        except sr.RequestError as e:
            print(f"请求错误; {e}")
            time.sleep(1)  # 短暂等待后重试
        except Exception as e:
            print(f"未知错误: {e}")
            time.sleep(1)

def main():
    """主函数"""
    print("语音指令监听已启动...")
    print("说 '菜单' 或 '文件' 来执行 Alt+F")
    
    # 启动语音识别线程
    speech_thread = threading.Thread(target=recognize_speech)
    speech_thread.daemon = True
    speech_thread.start()
    
    try:
        # 保持主线程运行
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        global is_listening
        is_listening = False
        print("\n程序已停止")

if __name__ == "__main__":
    # 确保pyautogui的安全特性开启
    pyautogui.FAILSAFE = True
    main()    