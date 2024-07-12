package com.flywings.xiangshi

import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.flywings.xiangshi.ui.theme.XiangshiTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        try {
            // 初始化 Chaquopy
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(this))
            }

            val py = Python.getInstance()
            val pyObject = py.getModule("main") // 加载main.py

            // 调用main.py中的函数，假设有个函数叫main_function
            val result = pyObject.callAttr("main_function").toString()

            // 打印调试信息
            Log.d("MainActivity", "Result from Python: $result")

            setContent {
                XiangshiTheme {
                    Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                        Greeting(
                            name = result,
                            modifier = Modifier.padding(innerPadding)
                        )
                    }
                }
            }
        } catch (e: Exception) {
            Log.e("MainActivity", "Error in setting content", e)
            // 发生错误时显示错误消息
            setContent {
                XiangshiTheme {
                    Scaffold(modifier = Modifier.fillMaxSize()) {
                        Text(text = "发生错误: ${e.localizedMessage}")
                    }
                }
            }
        }
    }
}

@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello $name!",
        modifier = modifier
    )
}

@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    XiangshiTheme {
        Greeting("Android")
    }
}
