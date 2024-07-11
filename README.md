# select-oblige-trial-zh-machine-translation
Madosoft（窗社）新作 SELECT OBLIGE 试玩版 gpt-4o 文本汉化补丁
### 简要说明  
因为翻译器用起来不太舒服，所以花了两个下午，用 gpt-4o API 做了个汉化补丁。  
由于本人能力和时间精力有限，这个汉化做得十分粗糙，几乎没有校对。人名可能会不统一，而且由于 gpt 时不时会不翻译而直接输出原文，所以可能会有少量漏译的情况，还请见谅。  
如果有大佬愿意校对的，欢迎提 PR。请在 **script-cn** 中修改。  
用到 [VNTranslationTools](https://github.com/arcusmaximus/VNTranslationTools) 进行格式转换。其余代码是用 gpt 写的，我自己 debug 了一下。存在不少问题，我把已知问题注释出来了，供参考。  
### 用法
将 releases 中发布的文件解压，将解压出的script文件夹放到游戏根目录即可。（这个游戏引擎是真方便，直接就能覆盖上去）
