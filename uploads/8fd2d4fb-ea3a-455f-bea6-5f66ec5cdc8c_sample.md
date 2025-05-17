

**学 士 学 位 论 文**

论文题目： **DESIGN AND DEVELOPMENT OF A BILINGUAL READER WITH ACCESSIBILITY FEATURES
无障碍双语语料阅读工具的设计与实现** 

姓    名：               **秦浩洋**               

学    号：            **201811580018**            

院    系：            **高级翻译学院**            

专    业：            **翻译（本地化）**          

指导教师：               **韩林涛**               

**二○二○ 年 五 月**



**Design and Implementation of Subtitle Making System for Translation Teaching Videos**


**by**

**Qin Haoyang**




**Supervised**

**by**

**Han Lintao**












**Submitted to the School of Translation and Interpreting**

**in partial fulfillment of the requirements for the degree of**

**Bachelor of Arts**

**at**

**Beijing Language and Culture University**






**Beijing, China**

**May 2022**

# <a name="_toc103080355"></a>**摘要**
无障碍（Accessibility），又称可及性、可访问性等，是用于描述环境、设施、信息与服务等各类主体的一种属性，具有该属性的主体应考虑到所有可能的用户与受众：包括残疾人、老年人以及出于各种原因无法以较普遍的方式参与相关活动的人群，通过更具适配性的设计与实现以让所有人都能更容易地行为与活动。

我国拥有规模庞大的残障人士群体，同时也在面临人口老龄化问题，社会对无障碍的需求不断扩大。随着信息技术不断发展，各种知识、内容的信息化水平不断提高，互联网早已成为人们学习知识、获取信息最常用，也是规模最大的“线上图书馆”，如何确保残障人士群体、老龄化人口能从互联网顺利获取信息已成为业界应当解决的问题。于是Web无障碍应运而生，我国也跟随世界上许多其他国家的脚步提出了自己的Web无障碍标准，相关的行业实践也在近年来有序展开。

在双语阅读和翻译学习领域，目前尚没有一个具有完善无障碍功能的网站存在。本研究与设计聚焦于无障碍领域下的“信息无障碍”与“Web无障碍”，结合在语言和翻译学习中扮演重要角色的双语语料阅读以及无障碍在Web应用中的设计实现，开发了一款带有无障碍辅助功能的、符合Web无障碍相关标准的、以Web应用为基础的双语语料阅读工具。

**关键词**：无障碍；信息无障碍；Web无障碍；双语阅读

i


# <a name="_toc103080356"></a>**Abstract**
Accessibility is an attribute used to describe subjects such as environments, facilities, information, services, etc. A subject with this attribute should consider all its potential users and audiences: including physically impaired users, elderly users, and users who for various reasons cannot participate in certain activities in the average way. It is usually implemented with various adaptive designs that can make its information or services more accessible for all users.

With a large demographic number of people with disabilities and the challenge of its aging population, the need for more accessibility practices in China is expanding. In the past three decades, China has witnessed the continuous development of information technology. All kinds of knowledge are being uploaded, shared, and created online, making the Internet the most commonly used and largest "online library" for people to learn knowledge and obtain information. It has now become a problem to be solved by the society and the industry, that how to ensure the disabled group and the aging population can equally obtain information from the Internet. Therefore, the idea of Web Accessibility was raised. China has followed the footsteps of many other countries in the world to put forward its Web Accessibility standards. In recent years, some industry practices on accessibility have also been carried out.

Currently, in the field of bilingual reading and translation learning, there is not yet an attempt to combine web technology with accessibility features. This research and design aim to make such an attempt. It focuses on "Information Accessibility" and "Web Accessibility" in the field of study. With the combination of the bilingual reading which plays an important role in language and translation learning, and the design and implementation of accessibility features in web applications such as screen speaking, font zooming, and closed caption, the research has managed to implement a design of an accessible bilingual reader based on web applications that meet related standards of Web Accessibility.

**Keywords:** Accessibility; Information Accessibility; Web Accessibility; Bilingual Reading




论文原创性声明

![ref1]本人郑重声明：所呈交的论文，是本人在导师指导下，独立进行的研究工作及取得的研究成果。尽我所知，除了文中已经注明引用和致谢的地方外，论文中不包含其他人或集体已经发表或撰写的研究成果，也不包含为获得北京语言大学或其他教育机构的学位或证书所使用过的材料。对本文的研究做出重要贡献的个人和集体，均已在文中以明确方式标明。本人完全意识到本声明的法律结果由本人承担。

签    名：\_\_\_\_\_\_\_\_

日    期：2022/6/10

学位论文知识产权权属声明

![ref1]本人郑重声明：本人所呈交论文，是在导师指导下所完成的，论文知识产权归属北京语言大学。学校有权保留并向国家有关部门或机构送交论文的复印件和电子版本，允许论文被查询和借阅，将论文编入有关数据库进行检索等。本人离校后发表或使用学位论文或与该论文直接相关的学术论文获成果时，署名仍为北京语言大学。

签    名：\_\_\_\_\_\_\_\_

导师签名：\_\_\_\_\_\_\_\_

日    期：2022/6/10

**Contents**

[Abstract in Chinese	i****](#_toc103080355)**

[**Abstract in English	2****](#_toc103080356)

[**1.**	**Introduction	1****](#_toc103080357)

[1.1 Literature Review	1](#_toc103080358)

[1.2 Significance of Research	2](#_toc103080359)

[1.3 Programming Languages and Tools	2](#_toc103080360)

[**2. Tool Design and Development	4****](#_toc103080361)

[2.1	Bilingual Reader’s Design and Development	4](#_toc103080362)

[2.1.1 Framing up Frontend	5](#_toc103080363)

[2.1.2 Scripting up Functions	7](#_toc103080364)

[2.1.3 Backend	9](#_toc103080365)

[2.2 Assistive Functions’ Design and Development	11](#_toc103080366)

[2.2.1 Screen Speaking	12](#_toc103080367)

[2.2.2 Adjustable Font	17](#_toc103080368)

[2.2.3 Closed Caption	18](#_toc103080369)

[2.2.4 High Visibility Cursor	19](#_toc103080370)

[**3. Application and Experiment	20****](#_toc103080371)

[3.1 Tests on PC	20](#_toc103080372)

[3.1.1 Test on Functions of Bilingual Reading Tool	20](#_toc103080373)

[3.1.2 Test on Accessibility	22](#_toc103080374)

[3.2 Test on iOS	26](#_toc103080375)

[3.2.1 Tests on Tool Functions	26](#_toc103080376)

[3.2.2 Tests on "VoiceOver" Compatibility	27](#_toc103080377)

[**4. Conclusion	28****](#_toc103080378)

[**References	28****](#_toc103080379)

[**Appendix	30****](#_toc103080380)








1. # <a name="_toc103080357"></a>**Introduction**
## <a name="_toc103080358"></a>1.1 Literature Review
<a name="_hlk103078291"></a>In terms of Web accessibility, the earliest efforts were made outside of China. In 1973, the first legislation related to Web accessibility made its debut in the United State. This legislation was *Rehabilitation Act*. Section 504 of this act legislated a series of requirements that must be followed when designing the website of the United States Department of Education. Later in 1998, the Rehabilitation Act Amendments of 1998 were published. In Section 508, accessibility rules were made for the producers of electronic devices and the providers of Web content. Right after that, in 1999, W3C joined to be another driving force in the promotion of Web accessibility. They put forward the Web Accessibility Initiative that later developed and published version 1.0 of Web Content Accessibility Guidelines (WCAG). In 2003, WCAG 2.0 was published to keep up with the latest progress of the Internet and computer science. For now, the latest WCAG is version 2.1 published in 2018. It is a staged result of the study made between 2003 and 2018, while more are expected to come in the future. Aside from the United States, many other countries have also published their own rules and legislation. For example, the British Disability Law of Britain, Disability Discrimination Act 1992 of Australia, and Accessibility of Public Websites – Accessibility for people with a disability: Council Resolution 2002 of the European Union.

In China, related efforts in the domain of information accessibility have started not long after the foundation of the People's Republic of China in 1949. For example, in 1953, the *New Scheme of Chinese Braille* (《新盲字方案》) was published to standardize the Chinese Braille System. Dongxiao Li, and Mengqi, Xiong have made a systematic analysis of the related rules and legislation with Natural Language Processing methods. However, related efforts on Web Accessibility in China started much later. A very comprehensive discussion was made about the subject in 2006, in which the author summarized quite an amount of the available information about Web accessibility back then. The author also made a practice by building up an accessible website with ASP.NET 2.0 framework (袁俊, 2006). In 2008, some experts focused on the accessibility problems of website navigation and proposed their solutions (陈子健, 2008). Another author studied the accessibility standards of website design for users with visual impairment in 2010 (赵英, 2010).

The studies mentioned above have all made quite some progress in terms of rules discussion and issue analysis. Several designs are also proposed to tackle the issues discovered. However, the studies are still short of up-to-date practice and implementation. In the internet industry of recent years, accessibility has gotten more attention. A new practice of providing assistive technologies within the website can be found on websites like Weibo, Zhihu, and the government website of Dubai. The technology behind this new practice, however, is lack discussion and is not publicly available.
## <a name="_toc103080359"></a>1.2 Significance of Research
<a name="_hlk103078361"></a>According to the *Communique of the Main Data of the Second National Sample Survey of Population with Disabilities* published in 2007, there are about 82.96 million people with disabilities in China. Combined with the data from the sixth national census in 2010 and the seventh national census in 2020, it is projected that there are about 87.42 million people with disabilities in China. It has now become an imminent issue how to ensure such a large number of people with disabilities can obtain information and learn knowledge from the Internet equally as average users. Meanwhile, the data of the 7th National Census shows that there are 264.02 million people over 60 years old in China, accounting for 18.70% of the total population. How to promote the Internet applications to provide an adaptive version for an aging population is of great social concern as well.

This study is dedicated to designing and developing a more user-friendly and accessible bilingual reader for elderly English learners or English learners that are physically impaired. Technological practices that are expected to be the solution to the two major issues mentioned above are included in this study. In addition, the study is also significant in the sense of making the practices and technology publicly available and easy to be deployed in future projects, by opening source the code.
## <a name="_toc103080360"></a>1.3 Programming Languages and Tools
<a name="_hlk103078402"></a>The code in this design can be divided into two sections, the frontend section, and the backend section. The frontend section mainly uses HTML, JavaScript, and CSS. Bootstrap is used to frame up the structure of the web pages, and jQuery is used as an enhancement to the basic JavaScript. The backend section mainly uses Python 3 as its major coding language. Flask framework of Python is used to construct the interface between the frontend and the backend. In addition, several SQL is embedded in the code written with Python to transfer data between backend and database.

In terms of tools, this research has chosen Google Chrome and iOS Safari as its web browser for tests. It uses MySQL to frame up the database. Another tool that is worth to be mentioned is "Accessibility Insights for Web". It is a testing tool that can facilitate the evaluation of web page accessibility level with a series of automatic tests and numerous guides for the manual test. More about this evaluation tool will be mentioned in chapter "Application and Experiment".

1\.4 Business Process

This tool is designed to contain 4 individual web pages, each serving an important purpose during the business process. For the general process, see the flowchart in Figure 1.1 below.


Figure 1.1 Flowchart of Business Process

`	`<a name="_hlk103079273"></a>For the database structure, see Figure 1.2 below. 


Figure 1.2 Database Structure

`    `<a name="_hlk103079432"></a>Users can enter the tool from "index.html" where entrances of other functions are displayed. Next, users can choose to access either "upload.html" or "filelist.html". On page "upload.html", users can upload their own file to read and fill out the form of file information. If users choose to upload a monolingual file, the file data will be machine-translated and split into sentences. If bilingual files are chosen to be uploaded, then files in both languages are split into sentences. After this, the split sentences will be written into the "sentencepool" sheet of the database, while the file information will be written into the "fileindex" sheet of the database. On page "filelist.html" users can find all of their uploaded files. Once a file is chosen, the tool will take the user to the page "reader.html". FILE\_ID will be used to determine which file's data should be retrieved from the database. At this point, users should be able to see the file content that they have chosen to read.

`    `For the accessibility assistive functions, the tool will provide a button toolbar on each page, so that the users can use the functions wherever they want. The settings made on one page will be retained even if users jump between the pages. They will not be changed or reset until users choose to do so.
# <a name="_toc103080361"></a>**2. Tool Design and Development**
<a name="_hlk103079509"></a>The development of the tool can be divided into two parts: the development of the bilingual reader and the development of the accessibility assistive functions. This chapter will introduce the design and development of both parts. For the bilingual reader part, this chapter will give a general introduction to the basic parts and put more weight on its unique features related to accessibility. And for the assistive function parts, this chapter will give a detailed introduction of how each function is implemented.
## <a name="_toc103080362"></a><a name="_hlk103079548"></a>2.1	Bilingual Reader’s Design and Development
This part of development can be divided into 3 steps. Step1: framing up frontend with HTML and Bootstrap. Step2: script up functions with JavaScript. Step3: use Python Flask to transfer and process data between front and backend. See Figure 2.1 below for the frontend structure of the design.


Figure 2.1 Frontend Structure
### <a name="_toc103080363"></a>2.1.1 Framing up Frontend
This section will focus on the HTML code of the tool. During the design process, several things like the frontend framework, layout, and use of color should be determined. Besides, once accessibility is included in consideration, some of the issues will require further analysis to meet certain criteria.

<a name="_hlk103079821"></a>2.1.1.1 Framework and Layout

The frontend framework in this design is Bootstrap, the most commonly used framework for responsive website design. It is a sharp tool for Web developers and is powering countless Web projects around the world. In this design, there are 4 major pages, the home page, the upload page, the file list page, and the reading page.

All pages have adopted the "top-to-bottom" layout, meaning that the major sections of a page are arranged in a vertical way and can be read from top to bottom. Within each major section, it follows the general "left-to-right" layout, meaning its paragraphs are arranged vertically from top to bottom as well, while each paragraph itself should be read horizontally from left to right. This type of layout is easy to understand and can be smoothly navigated through by most users.

<a name="_hlk103079965"></a>2.1.1.2 Color and Accessibility

Color is one of the major subjects in Web Accessibility. Good use of color makes elements in a website more distinguishable and thus makes the website more accessible to users. However, poor use of color may make it rather hard for some users to distinguish the elements on a page and cause accessibility failure. There are two major things to be considered when it comes to color accessibility: adequate contrast and delivery of information. In WCAG 2.1 AA minimum criterion, it is required that the color contrast ratio between average text and its background should be at least 4.5. For large text, this ratio can be lower at 3.0. In the enhanced contrast criterion, the color contrast ratio between average text and its background should be above 7.0. And for large text, this ratio should be above 4.5. Besides, color should not be the only thing that conveys messages or information and there should always be an alternative visual indication such as text or pattern. That's because some visually impaired users may not be able to distinguish between two or several colors, or can only discern the luminance but not any color. If the contrast between the color of text and its background is low, some users may not even be able to see it. While if color is the only method that is conveying a piece of information, it may not be received at all. If both of these requirements are met, elements on a web page will get higher visibility, which would benefit all users.

The formula that calculates the contrast radio is listed below:

r=(L1+0.05)/(L2+0.05)

In this formula, L1 refers to the relative luminance of the lighter color, L2 refers to the relative luminance of the darker color, and the result* r* refers to the luminance contrast. For a color value described in sRGB color space, the formula that calculates a color's relative luminance L is listed below:

L = 0.2126 × R + 0.7152 × G + 0.0722 × B

While in this formula, the value of R, G, and B are calculated with the formulas listed below:

if RsRGB≤0.03928 then R=RsRGB12.92 else R=RsRGB+0.0551.0552.4

if GsRGB≤0.03928 then G=GsRGB12.92 else G=GsRGB+0.0551.0552.4

if BsRGB≤0.03928 then B=BsRGB12.92 else B=BsRGB+0.0551.0552.4

In these three formulas, RsRGB, GsRGB, BsRGB can be calculated in the formula listed below:

RsRGB=R8bit/255

GsRGB=G8bit/255

BsRGB=B8bit/255

In these formulas, R8bit,  G8bit,  B8bit refers to the decimal value of red, green, blue part in a color value described in sRGB color space. Take #2329d6 for example, its R8bit=35, G8bit=41, B8bit=214, thus its RsRGB=0.1372549, GsRGB=0.16078431, BsRGB=0.83921569, thus its R=0.01680738, G=0.02217388,B=0.67244316, its L =0.06798241. When compare to white(#ffffff), the contrast ratio r=8.89 (All formulas above are originally from WCAG 2.1 Understanding Success Criterion 1.4.1: Use of Color). 

The three major colors used in this bilingual reader are black (#000000), white (#ffffff), and a type of indigo blue (#2329d6). Thus, there are 3 possible combinations of color: black and white, black and blue, white and blue. The blue color (#2329d6) and white(#ffffff) can be used as each other's background and text due to their contrast ratio being 8.89, above the 7.0 bar. Black can only be used when white is the background color because its color contrast ratio with white color is the highest possible value at 21.0, while its ratio with the blue color is rather low at 2.35.
### <a name="_toc103080364"></a>2.1.2 Scripting up Functions
For the bilingual reader, there are two things worth mentioning in the JavaScript part of the code. The first is an alternative way of handling the submit action of the form. And second is the template rendering method used on the reading page.

2\.1.2.1 An Alternative Way of Submit Action

When using the Bootstrap framework, if a form has a "<button>" element with its "type" attribute set as "submit", it will listen for the event of pressing down "Enter". Once a user presses the key "Enter" when filling out the form, it will trigger the button of type "submit", which will submit the form and jump to another page. However, what comes together with this feature is a problem. The event of pressing down "Enter" is also the keyboard action that users can use to interact with elements such as links, buttons, text areas, inputs, etc. For average users who can interact with elements in a form (usually "<input>" element) by mouse click, this won't affect much of their experience. But for the users who have to use a keyboard to navigate through the Web elements, this is a clickbait that may cause inaccessibility. An alternative way to achieve submit action is to rewrite the action with JavaScript. See Figure 2.2 below:


Figure 2.2 Function "getForm()"

In the code above, it can be seen that the rewritten submit action is named "getForm()". It first defines a variable named "form", and sets the value of the variable with the data from the form. Then it posts the data with an ajax module to the backend address, where the data will be processed and saved into the database. 


Figure 2.3 Button with "onclick" Event Assigned

In the HTML code shown in Figure 2.3, the original button of type "submit" is now substituted with another button without type attribute, but its "onclick" will not trigger the default submit function, but the "getForm()" function mentioned above.

2\.1.2.2 Reading Page

The design of the reading page of this tool uses the method of template rendering, which is implemented through the jQuery Validate plugin. The page itself and its HTML code are displayed in Figure 2.4 and Figure 2.5. It is a combination of a navigation bar and a blank list, with several placeholders such as "{0}","{1}","{2}". 



Figure 2.4 Reading Page with Placeholders


Figure 2.5 Code of Template in the Reading Page

`    `The placeholders in the HTML code above can be recognized by the function "$.validator.format()" of jQuery Validate. This function can substitute the placeholders with other customized data. And in the design of the bilingual reader, the placeholders are substituted with the sentences in the database.


Figure 2.6 Code of Template Substitution

In the code shown in Figure 2.6 above, it first defines a variable "html\_template" and sets its value with the HTML code of the template row of the blank list. Then it uses "validator.format()" function to substitute the placeholders with customized data and return a string, which can be appended to the original HTML code.
### <a name="_toc103080365"></a>2.1.3 Backend
The backend code of the tool is written with Python 3 Flask. It is a powerful Python module that can be used to transfer data between the frontend and the database. For example, this tool has transferred data for display on the file list page and the reader page. It has also transferred and processed data from the frontend to the backend on the upload page. What's worth discussing about this part, however, is the sentence splitting function based on Regular Expression.

2\.1.3.1 Sentence Splitting based on Regular Expression

Regular Expression is a powerful tool that can be used to perform basic Natural Language Processing on a certain string of text. It is based on text pattern matching and is widely used as a versatile easy-to-learn tool in the internet industry. In the current design, Regular Expression is used to split the text file into sentences.

In Python, splitting sentences is not that big of an issue. Because there are quite some ready-to-go options and Regular Expression is not among the handiest tools. For example, there is "re.split()" function which is from the Python's Regular Expression module "re", and there is "sent\_tokenize()" function from the famous NLP module "nltk". With one line of code, these two functions can return a list of sentences split from a large chunk of text, but with some flaws.

For the "re.split()" function, it can only split sentences with a designated character as its sentence boundary. For example, give a paragraph like this: "It is getting funny. I need more time to think about this… By the way, do you have any idea about this? I would really love to hear some of your opinions.", and process it with "re.split('.')", it will make a split in the sentence wherever there is a character '.', thus returning a list like this:"['It is getting funny', 'I need more time to think about this', 'By the way, do you have any idea about this? I would really love to hear some of your opinions']". The problems are evident. First, it couldn't split the sentence at other sentence full stops like '?'. And second, it loses all the '.' character in the paragraph.

For the "sent\_tokenize()" function, it can perfectly split all the sentences at single-character full stops and preserve the full stop character in the split sentences, but it can only split text in English, not in Chinese or any other language, making it hard to perform sentence splitting on bilingual text.

To solve the problems mentioned above, 7 lines of code are used. See Figure 2.7 below for the code:


Figure 2.7 Code of Sentence Splitting Regular Expression

These lines of code are further developed from a segment of the open-source project "HarvestText". It mainly uses the "re.sub(parameter1, parameter2, parameter3)" function to perform the splitting. It can look through a piece of text specified in parameter3, search for patterns specified in parameter1, and substitute the pattern with another pattern specified in parameter2. The first line of code searches for all the "\n" in a piece of text and deletes them, gathering all paragraphs in the text into one long paragraph. The second line of code matches all the single full stops that are not followed by any type of backquote or back bracket, appending a "\n" to each of them. The third line matches all the places where there is one or more "." (such as a period mark or ellipsis dots in English) that are not followed by any type of backquote or back bracket, appending a "\n" to each of them. The fourth line matches ellipsis marks in Chinese "……" that is not followed by any type of backquote or back bracket, appending a "\n" to each of them. The fifth line matches all the full stops that are followed by a backquote or back bracket, appending a "\n" to the backquote or bracket. The sixth line removes the "\n" at the very end of the long paragraph if there is any. And finally, the seventh line split the long paragraph at all the "\n", returning a list containing all the sentences.
## <a name="_toc103080366"></a>2.2 Assistive Functions’ Design and Development
Assistive functions make up a big part of the tool development. It has adopted the latest practice in the internet industry of combining the assistive function into the website with JavaScript functions and provided a portable version of the technology. This part of the code can be divided into 4 sections: the screen speaking section, the adjustable font section, the closed caption section, and the high visibility cursor section. For the general structure of the assistive functions, see Figure 2.8 below.


Figure 2.8 Accessibility Assistive Functions' Structure

`    `For the frontend display of the assistive technologies, see the figure below.


Figure 2.9 Frontend Display of Assistive Functions
### <a name="_toc103080367"></a>2.2.1 Screen Speaking
Screen speaking plays an important role in most, if not all, assistive technologies. For a Web app, the majority of information is delivered visually, thus making it virtually impossible for visually impaired users to get information equally well as average users without others' help. Screen speaking, however, can transfer visual content into a vocal format. Though not as vivid as the visual representation of information, screen speaking makes a zero-to-one breakthrough for certain groups of users to get information, thus allowing more users to access some of the web-related services like mobile payment. It is also a very useful feature for average users in certain contexts where visual contact with the screen is not possible or less required, such as road navigation and book reading.

In this design, screen speaking is implemented with two speech related interfaces of Web API, "SpeechSynthesis" and "SpeechSynthesisUtterance". Combining these two interfaces with keyboard navigation of the webpage, the tool can speak bilingual text in Chinese and English when hovering the mouse on a certain element or focusing on an element with keyboard actions. It also has 2 independent switches to change its speaking speed and speaking mode.

2\.2.1.1 "SpeechSynthesis" and "SpeechSynthesisUtterance"

The Web API "SpeechSynthesis" and "SpeechSynthesisUtterance" are the two major interfaces that can be used to control speaking services on certain devices. In this case, the device is a web browser. It is important to mention that, although these two features are supported in most of the mainstream browsers, they are still regarded as features under development, meaning that they are not supported in a couple of browsers like Internet Explorer on PCs or Android Opera on mobile devices. See Figure for detailed browser compatibility information. 


Figure 2.10 Browser Compatibility of Web API "SpeechSynthesis"

For the code that uses these two interfaces, see the Figure below.


Figure 2.11 Code with Speech Related API

In the code, "SpeechSynthesisUtterance" is used to construct an object "speaker" that receives values of several attributes, including "text", "lang", and "rate". The attribute "text" contains the content to speak; "lang" defines the speaking language; "rate" defines the speaking speed. 

This object will be used in the functions of "SpeechSynthesis" as a parameter, while the function performs corresponding actions based on the attribute values of the object. Function "window.speechSynthesis.cancel()" is used to clear the queue of utterances, stopping all the speaking actions that are being or to be performed. Function "window.speechSynthesis.speak(object)" is the function that lists an utterance into the queue. To make the speaking action more responsive, the function "speakText()" is defined. Whenever it is triggered, it would first use the function "window.speechSynthesis.cancel()" to clear the queue, thus performing the new utterance immediately.

2\.2.1.2 Keyboard Navigation

When screen speaking is turned on, users can use "tab" and "shift+tab" on keyboard to navigate through all elements that conveys visual information, including "<a>", "<p>", "<span>", "<h1>", "<h2>", "<h3>", "<h4>", "<h5>", "<h6>", "<img>", "<input>", "<button>", "<label>", "<select>". This function is achieved with two lines of code shown in Figure below.


Figure 2.12 Code of Keyboard Navigation

`	`The code is written with jQuery, JavaScript. The first line defines a variable containing all the tag names that may contain readable information. While in the second line, the "$(speakTags)" is a jQuery selector that selects all the elements wrapped in the tags mentioned in the variable "speakTags". The function "attr(parameter1, parameter2)" can edit the attribute specified in parameter1 of the selected elements, changing its value to the value specified in parameter2. In this case giving all the selected elements' attribute "tabindex" a value "0".

`	`The attribute "tabindex" is used to control if an element in the webpage is focusable with keyboard action "tab" and "shift+tab". When an element's "tabindex" is set as "0", it means the element is focusable with a keyboard but without a specific order. In this case, if a user navigates through the page that contains the element with "tab" and "shift+tab", the focusing sequence is determined by the natural structure of the page. When an element's "tabindex" is set as "-1", it means the element is not focusable at all. In this case, if a user navigates through the page that contains the element with "tab" and "shift+tab", the element will not be focused. When an element's "tabindex" is set as "1", it means the element is focusable with a keyboard and is always the first one to be focused. In this case, if a user navigates through the page that contains the element with "tab" and "shift+tab", the element will be the first one to be focused even if it is located at the bottom of the page.

`	`With the details mentioned above, it is now pretty clear that with the code shown in Figure 2.12, all elements wrapped in the tags mentioned in the variable "speakTags" are made focusable with keyboard action "tab" and "shift+tab". The focusing sequence is the natural sequence of the elements in the HTML code.

<a name="_hlk102483215"></a>2.2.1.3 Text and Event for Speaking

To finally implement screen speaking, two things are required: the text content for speaking and the event to trigger the speaking. In this tool, the text content is designed to be the combination of the element tag name, element text, and additional information contained in element attributes (e.g., attribute "alt" of <img> element). Events that trigger the speaking would be "focus" and "mouseenter".

For the code that gets text content for speaking, see Figure 2.13 below.


Figure 2.13 Code of Text for Speaking Retrieval

`    `The variable "speakTags" is also used here to select all the elements that 

contain text to be spoken. Besides, there is another list variable named "tagTextConfig" with several "key: value" pairs. Each of these pairs has a tag name as its key and the tag name's description in Chinese as its value, which will be later used to combine into the text content.

`	`Function "getTagText(el)" will take one element "el" as its parameter. Inside the function at line 11, the tag name of element "el" is given to the variable "tagName". From line 13 to line 19, if "tagName" equals "input", then the variable "tagName" is added with its "type" string to further categorize its name. In line 21, the function returns the value in tagTextConfig whose key equals "tagName" with a space appended. If the "tagName" is not a key that exists in tagTextConfig, the function returns an empty string with a space appended.

`	`Function "getText(el)" will also take one element "el" as its parameter. It will call on the function "getTagText(el)" to get the tag's description in Chinese first, append to it the element's "title", "alt", and "innerText" if existent, and finally return this combination as the element's text content for speaking. When "el" is an element "select", the case is a little unusual. Because in common senses, the "innerText" of an element "select" should be the text of its selected option. However, with several tests it is easy to find out that the value of "innerText" of an element "select" is all the text wrapped in the "<select>" tag pair, that is, the text of every option, regardless of being selected or not. To get the text of its selected option, a unique index can be made use of: the "checked" attribute of the element "option". In the element "select", the selected option will be given a "checked" attribute. Therefore, according to the common senses, code line 25 to line 27 can be written: if "el" is a "select" element, the code would get the one children "option" element of "el" who has an attribute "checked" and take its text as the select element's text.

`	`As mentioned above, the events that trigger speaking are "focus" and "mouseenter". With the code shown in Figure 2.14 below, it is finally made possible to speak the elements in the webpage.


Figure 2.14 Code of Speaking Events

`	`From line 1 to line 5, the code selects all the elements wrapped in tags mentioned in "speakTags", giving them an event "onmouseenter", which would trigger a function to speak the element text returned by "getText()" when the mouse enters these elements. From line 6 to line 10, the code does basically the same thing, except the event is "onfocus", which is triggered when an element is focused by either keyboard actions or mouse actions.
### <a name="_toc103080368"></a>2.2.2 Adjustable Font
In this tool, the font is made adjustable by clicking two buttons of the assistive functions. Users can change both font size and font-background color combinations. Font size can be switched between Both of these two functions are designed to further strengthen the visibility of elements that contains text and thus increasing the accessibility of the tool.

2\.2.2.1 Adjustable Font Size

In HTML, the font size of an element's text is controlled by the attribute "font-size". In section 2.2.1.2 Keyboard Navigation, a variable "speakTags" has been defined to select all the element tags that may wrap text, which can also be used here to select the elements and control the font size of the text. For code that implements this function, see the figure below.


Figure 2.15 Code of Text Enlargement

`	`As mentioned in section 2.2.1.2, "$(speakTags)" is a jQuery selector that selects all the elements wrapped in the tags mentioned in the variable "speakTags". The function ".css(parameter1, parameter2)" is used to control the CSS of the selected element(s). In this case, parameter1 is "cssText", meaning the function aims to change the style of text. Parameter2 is "fontsize-size:30px!important", meaning that the function will change the style property of "font-size", setting its value as "30px", and use the appendix "!important" to overlook all other incoming value of "font-size".

`	`With the code above, it is now possible to enlarge the font size of all text on a page. And by reversing the logic, it would be easy to reset the text to its original size. See the code shown in the figure below.


Figure 2.16 Code of Font Size Reset
### <a name="_toc103080369"></a>2.2.3 Closed Caption
Closed Caption, sometimes referred to with its abbreviated form "CC", is a technology widely used nowadays to turn audio information into visually receivable information (usually text). For average users, it usually serves the same purpose as the traditional subtitle, that is, to convey the audio information clearer by printing it out in text form. However, "CC" has its own unique purpose. In some cases, "CC" is also referred to as "descriptive caption", indicating that it is meant to describe the context of audio information as well. In a movie, for example, such context might be background music, environment sound, tone of speaking, etc. This technology is originally designed to help users with hearing loss get audio information, thus increasing the accessibility level. Today, this technology is also helping average users to better receive information in both video and audio form. For example, the ASR captioning of audio messages in WeChat and ASR CC on Netflix and YouTube.

Before being implemented, this feature requires two things: the text content for caption and some space to display the content. The text content for captioning is also generated with the function "getText()" mentioned in section 2.2.1.3 Text and Event for Speaking, since the generated text is regarded as descriptive. In terms of the space for displaying, the tool has a hidden "<div>" element that sticks to the bottom of the browser window. See the figures below for its HTML and JavaScript code.


Figure 2.17 Code of Closed Caption Display Area


Figure 2.18 Code of Closed Caption Events

`    `In the HTML code, the "div" element is assigned with an id "#accc" and a "class" value "d-none". The class "d-none" is a predefined value in Bootstrap used to hide the element, and the id "#accc" is used to select the element. In the JavaScript code, it first selects the element with the id "#accc", and removed the class value "d-none" to reveal the element.

`	`From line 2 to line 7 and from line 8 to line 13, the code is similar to that mentioned in section 2.2.1.3 Text and Event for Speaking. Assigning two events, "onmouseenter" and "onfocus", to the elements that need to display closed caption. When these two events are triggered, a function will get the descriptive text with the function "getText()" and display it in the element "#cccontent", children of element "#accc".
### <a name="_toc103080370"></a>2.2.4 High Visibility Cursor
In Web App, it is possible to customize the style of the mouse cursor. For the users who have impaired vision but can still see the movement of the cursor, a customized cursor would be helpful. The original auto cursor of a Web browser is small in size and usually white in color, which has a very low contrast ratio to the background. To increase the visibility of the cursor, it is viable to either enlarge the cursor or change the cursor color. With the code shown in the figure below, it is possible to change the cursor into a large black one. 



Figure 2.19 Code of High Visibility Cursor Switch

See the difference between the default cursor and high visibility cursor in the figure below.


Figure 2.20 Comparison between Default and High-visibility cursors
# <a name="_toc103080371"></a>**3. Application and Experiment**
Experiment and testing also make up a large part of the tool's development. In order to get a better knowledge of the tool's performance and level of accessibility, multiple tests were carried out, focusing on both the overall performance of the tool and each of the features' usability. During the test, some issues were also uncovered. This section will focus on these issues and propose potential solutions to them.
## <a name="_toc103080372"></a>3.1 Tests on PC
Since the tool itself is dedicated to the PC platform and web browser, most of the tests are run on PC. Generally speaking, there are two major tests: the test on functions of the bilingual reading tool and the test on accessibility.
### <a name="_toc103080373"></a>3.1.1 Test on Functions of Bilingual Reading Tool
This part of the test is performed manually, by three developers with previous experience in Web App development. For the general result, please see the table below.

Table 1 General Result of Tool Function Tests

|Function Name|Count of Issue|Severity|
| :-: | :-: | :-: |
|Feature Introduction|None||
|Feature Entrances|None||
|Information Form|None||
|File Input|1|P1|
|List Display of Files|None||
|Reading Entrances|None||
|File Search|None||
|List Display of Sentences|1|P1|
|Word Select & Look Up|1|P2|

In the first column of this table, all the basic functions of the tool are listed. And in the second column, the number of issues uncovered during the test of each function is listed. The third column contains the severity of the issue. P1 means that the issue is relatively severe and may cause a usage barrier. P2 means that the issue is less severe and can still be used, despite not reaching the expected effectiveness. In the following small sections, the issues will be discussed in detail.

3\.1.1.1 File Input Issue

When uploading a file, users may choose randomly among many .txt files. Some of the files may be named in English, while others in Chinese or other languages. Once the file is uploaded, it will be processed by several lines of code in the backend to give it a new unique file name and save it in the upload directory of the project. See the code in Figure 3.1 below:


Figure 3.1 Code of File Saving

`	`These 15 lines of code will first get the file name of the original uploaded file, retaining its filename extension to combine with a unique new name consisting of time and a random value. In this way, the user can upload the same file multiple times without being proposed with the system error of a duplicate file name.

`	`When testing this function, however, it always proposes an IndexError: list index out of range on line 6 when the uploaded file has a name in Chinese, meaning that there is only one or less element in the returned list of "file\_name.split('.',1)[1]". By printing out the returned list, there is only one element "txt" in it. 

With some research, the issue was finally located at the function "secure\_filename()" on line 2. This function only returns values in ASCII, and apparently, Chinese characters are not among them.

One way to address this issue is to change the file name that contains Chinese characters before letting function "secure\_filename()" process it. A third-party module of Python named "pypinyin" may achieve this. See the code in Figure 3.2 below.



Figure 3.2 Code of "pypinyin"

`	`The module "pypinyin" is a powerful tool to perform NLP related to Chinese pinyin. The specific function "lazy\_pinyin(string)" can process any given string. If the string contains Chinese characters, it will swap each of the Chinese characters into simple pinyin in English letters and return a list of pinyin and other content in the string. Finally, by joining the list with no space in between, the function "secure\_filename()" would both receive and return a filename written with English letters, which is totally ASCII compatible.

3\.1.1.1 List Display of Sentences Issue

`    `Once a user has uploaded a file into the tool, the file should be displayed on the file list page, where it can be searched and accessed. If a user only uploaded the source file, machine translation will be used to translate the source sentences. Finally, the code will upload the source sentences and target sentences to the database. See Figure 3.3 below for the code.



Figure 3.3 Code of File List Display

`	`The issue occurs when some of the translated sentences are uploaded, but the database refuses the SQL query. This is caused by unescaped characters. Some of the machine translation results may contain characters such as a single quote or backslash "\". These characters have special meanings in the SQL syntax and must be escaped when they exist in a string. Function "escape\_string()" of the module "pymysql" may suitable for this. See the code in the Figure below.
### <a name="_toc103080374"></a>3.1.2 Test on Accessibility
This part of the tests contains automatic scanning tests of the HTML code, manual test of action accessibilities, and manual test of compatibility with outside assistive technologies (Windows Narrator). The first two tests are run in "Accessibility Insight for Web".

3\.1.2.1 Testing with "Accessibility Insight for Web"

To test the accessibility of the tool, a third-party plugin named " Accessibility Insight for Web " is used. This testing plugin can both scan the code automatically and guide related manual tests. There are 24 major testing items in the tool, each concerning an important aspect of accessibility. For the general result of the tests, see the Figure below. 

Table 2 General Result of "Accessibility Insight for Web" Tests

|Test Item|Count of Issue|Severity|
| :-: | :-: | :-: |
|Automated checks|8|P2|
|Keyboard|None||
|Focus|None||
|Landmarks|None||
|Headings|None||
|Repetitive content|None||
|Links|None||
|Native widgets|None||
|Custom widgets|None||
|Time events|None||
|Errors / status|None||
|Page navigation|None||
|Parsing|6|P2|
|Images|None||
|Language|None||
|Sensory|None||
|Adaptable content|1|P1|
|Audio / video|N/A (No matching instance)||
|Multimedia|N/A (No matching instance)||
|Live multimedia|N/A (No matching instance)||
|Sequence|None||
|Semantics|None||
|Pointer / motion|None||
|Contrast|9|P2|

3\.1.2.1.1 Issues in "Automated check"

Issues in the item "Automated check" are basically the same as those in the item "Contrast", all concerning the color contrast of text and icons in the buttons the assistive functions. These buttons have adopted the default color scheme (white and a type of light blue <a name="_hlk102745519"></a>#0d6efd) of Bootstrap ".btn-out-primary", which has a color contrast ratio of 4.5. This is just enough for larger buttons and text, but for average text with smaller font size, the recommended color contrast ratio is at least 7.0. Changing the default CSS code of Bootstrap, and swapping the light blue color (#0d6efd) into the customized indigo blue (#2329d6), will increase the color contrast ratio to 8.89. See the code in the Figure below.



Figure 3.4 Code of Color Changing in CSS

3\.1.2.1.2 Issues in "Parsing"

Issues in the item "Parsing" are about ARIA-related attributes. With the help of a testing website published by W3C named "Nu HTML Checker", all the related problems can be easily discovered. See the checking results in the Figure below.



Figure 3.5 Reults from "Nu HTML Checker"

`	`In the figure above, the "Warning" tag means there is a potential error concerning the highlighted code, while the "Error" tag means there is a certain error. By editing the code according to the given suggestion, these issues would be easily fixed.

3\.1.2.1.3 Issue in "Adaptable content"

`    `The issue in the item "Adaptable content" is mainly about the content display of the page in low resolution. When the web page is displayed under the resolution of 1280\*1024, links and buttons in the navigation bar are not displayed. To solve this, an alternative way of collapsing the links and buttons into a ".offcanvas" element is valid to solve this issue.

`	`3.1.2.2 Windows "Ease of Access" Compatibility Test

`	`Windows system has a set of built-in accessibility assistive functions. It can be found in Start - Settings - Ease of Access. These functions include Magnifier, Color Filter, High contrast, Narrator and Closed captions, etc. Users with certain types of impairment may use the functions to navigate through a computer of Windows system. It is important for a Web App to be compatible with these functions. Therefore, a series of tests were carried out to verify the "Ease of Access" compatibility of the tool. See the general test results in the table below. Closed Caption provided by Windows only works on videos, thus marked as "N/A(Not Applicable)".

Table 3 General Result of Windows "Ease of Access" Compatibility Test

|Test Item|Count of Issue|Severity|
| - | :-: | :-: |
|Magnifier|None||
|Color Filter|None||
|High Contrast|1|P2|
|Narrator|1|P1|
|Closed Caption|N/A (Not Applicable)||
`    `3.1.2.2.1 Issue in "High Contrast"

`    `The issue in the testing item "High Contrast" is regarding the icon and image color. Once the High Contrast is activated, the system will automatically change the current color scheme of text, hyperlink, button, and background into a predefined high-contrast scheme. Images, however, have solid color to themselves and won't be affected by the new scheme. If the image serves any non-decorative purposes and doesn't have a text alternative, the changed background color may incur a drop in the color contrast ratio, which could cause an accessibility issue. 

`	`To address this issue, it is viable to always provide a text alternative for images. This may not directly increase the images' color contrast ratio to the background, but the message will be delivered.

`    `3.1.2.2.2 Issue in Narrator

`	`This issue is caused by the screen speaking strategy of the Narrator. For the content displayed in a web browser, the Narrator would only read the text in the link, button, and input elements. Other elements like paragraph, span, and images are not spoken. Since the tool is meant to display texts for reading, this issue may make the tool not usable for some users.

`    `By comparing Narrator with other voice assistive functions, such as Talkback of Android and VoiceOver of iOS, this issue is only occurring in Windows Narrator. It would be great if Window Narrator can make some improvements. But for now, for users who are using Windows Narrator to navigate through the tool, it is viable to turn on the accessibility assistive function and screen speaking with the help of the Narrator, then turn off the Narrator during using the tool. The built-in assistive function of the website will be able to help the user to acquire information from the tool.
## <a name="_toc103080375"></a>3.2 Test on iOS
"iOS" is the factory-issued operating system of every iPhone in the world. This particular system has probably one of the best accessibility designs in the world. For users that are visually impaired, the iOS system can provide a great experience of browsing content with a mobile phone.

In these tests, the tool will be run on an iPhone 13 with its iOS updated to version 15.4.1. Two types of tests will be performed: tests on functions of the tool and tests on "VoiceOver" compatibility.
### <a name="_toc103080376"></a>3.2.1 Tests on Tool Functions
Table 4 General Result of Tool Function Tests

|Function Name|Count of Issue|Severity|
| :-: | :-: | :-: |
|Frontend Display|1|P2|
|Feature Introduction|None||
|Feature Entrances|None||
|Information Form|None||
|File Input|None|P1|
|List Display of Files|None||
|Reading Entrances|None||
|File Search|None||
|List Display of Sentences|None|P1|
|Word Select & Look Up|1|P2|

3\.2.1.1 Issue in Frontend Display

The size of the screen varies across all kinds of devices. A web app should be able to adapt to different screen sizes and display content at a proper scale. If a web app's content displays properly on a PC but is not adaptable to small size screens, the content would be displayed at a very small scale, incurring a loss of visibility. 

By adding a line of code to the head of HTML files, this issue can be easily addressed. See the code in the Figure below:



Figure 3.6 Code of Screen Size Adaptation

This line of code would automatically adapt the content of a web app to the screen size of the device, and make sure the elements on a web page are displayed at a proper scale. 
### <a name="_toc103080377"></a>3.2.2 Tests on "VoiceOver" Compatibility
VoiceOver is the major accessibility feature in iOS, and it is probably the most elaborate built-in accessibility assistive feature. It was first deployed on macOS, the PC operating system of Apple Inc, aiming to make PC accessible for users with vision impairment. But the company didn't stop right there. They continued to enhance the versatility of the feature. Soon enough was it deployed on iOS, and later on other operating systems and product lines of the company. In some special product lines, for example. the iPod Shuffle series, VoiceOver even became the major method of conveying messages. Today, VoiceOver and Apple products are helping a large body of users with all kinds of impairments to enjoy digital content more equally.

In this part of test, VoiceOver is called up to navigate through each page of the tool, and click on every button. See the general result in the table below.

Table 5 General Result of iOS "VoiceOver" Compatibility Test

|Test Item|Count of Issue|Severity|
| - | :-: | :-: |
|index.html|None||
|filelist.html|None||
|upload.html|None||
|reader.html|None||
|Introduction.html|N/A (Not Applicable)||
As shown in the table above, thanks to the well-designed "VoiceOver" and the accessible page, the test went smoothly with no issues (such as invisible focus point and negation of focusable item), meaning the tool is compatible with "VoiceOver" of iOS.

# <a name="_toc103080378"></a>**4. Conclusion**
In conclusion, this tool has achieved the basic purposes of an accessible bilingual reader. It has also made some adequate progress in terms of function and design philosophy. In addition, there is a couple of aspects that could use some improvement in the future.

It has passed the tests run on the tool named Accessibility Insight for Windows with a few issues, meaning that it has basically met WCAG2.0 AA standards. The tool is also compatible with other accessibility assistive technologies such as VoiceOver of the iOS system and the Narrator of Windows.

` `It has provided an open-sourced, portable version of code that implements accessibility assistive functions on websites. Other developers may also use the code in their own projects and deploy the accessibility features with ease. Besides, it is also a creative idea of letting the impaired users teach themselves, especially teaching themselves English as a second language, with a tool that is designed to be accessible. Future works from other developers may take this idea as a basis, and expand it from bilingual learning to multilingual learning, even to subjects beyond language study.

One aspect that can be improved about the tool is its accessibility autonomy. For example, when uploading documents, it requires a series of actions in a window propped by the computer system instead of the web browser. Such windows are out of the control domain of the accessibility assistive functions of the current tool. If the user is not using an agent with needed accessibility features or other assistive technologies, this may cause inaccessibility. 

Another aspect of possible improvement is its content source. Currently, the tool still requires the user to upload their own materials to read. For a certain group of users, especially users with certain types of physical impairment, getting these materials might be as challenging as reading them. It would be a great idea to connect the tool with some information source that can keep feeding the reader with up-to-date content in text format. A powerful candidate for this would be RSS (Really Simple Syndication).


# <a name="_toc103080379"></a>**References**
1. 陈子健,孙祯祥.信息无障碍视角下网站的导航设计[J].图书情报工作,2008,52(09):6-8+31.
1. 陈子健,孙祯祥,张燕.从网络信息无障碍的角度探讨缩小数字鸿沟[J].情报理论与实践,2009,32(01):41-43+29.DOI:10.16353/j.cnki.1000-7490.2009.01.032.
1. 第二次全国残疾人抽样调查主要数据公报（第二号）[EB].2007.Retrieved from国家统计局: http://www.stats.gov.cn/tjsj/ndsj/shehui/2006/html/fu3.htm
1. 第七次全国人口普查公报（第二号）[EB].2021.Retrieved from国家统计局:http://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202105/t20210511\_1817197.html
1. 第六次全国人口普查主要数据发布[EB].2011.Retrieved from 国家统计局: http://www.stats.gov.cn/ztjc/zdtjgz/zgrkpc/dlcrkpc/dcrkpcyw/201104/t20110428\_69407.htm
1. *iPhone 使用手册*[Z].2021.Retrieved from Apple - 官方网站: https://support.apple.com/zh-cn/guide/iphone/welcome/ios
1. *Web Speech API - Web API 接口参考|MDN* [Z].2021.Retrieved from MDN Web Docs: https://developer.mozilla.org/zh-CN/docs/Web/API/SpeechSynthesis
1. *Windows 的辅助功能支持*[Z].2022.Retrieved from Microsoft: https://support.microsoft.com/zh-cn/windows/windows-的辅助功能支持-8b1068e6-d3b8-4ba8-b027-133dd8911df9#WindowsVersion=Windows\_10
1. 袁俊.面向建设无障碍网站的Web可访问性研究与应用[D].重庆大学,2006.
1. 赵英,张培宾.针对视障人士的Web无障碍网站标准及设计研究[J].情报杂志,2010,29(04):138-141+168.
1. 赵英,章梦玄.老年视障人士信息无障碍网站设计[J].中国老年学杂志,2018,38(02):473-477.
1. *Accessibility Insights for Web* [Z].2022.Retrieved from Accessibility Insights: https://accessibilityinsights.io/docs/web/overview/
1. CaldwellBen, ReidGuarinoLoretta, VanderheidenGregg, ChisholmWendy, SlatinJohn, & WhiteJason.*WCAG 2.1* [Z].2018.Retrieved from W3C: https://www.w3.org/TR/WCAG21/
1. ChisholmWendy, SlatinJohn, & WhiteJason.*WCAG 2.0* [Z].2008.Retrieved from W3C: https://www.w3.org/TR/WCAG20/
1. ChisholmWendy, VanderheidenGregg, & JacobsIan.*WCAG 1.0* [Z].1999. Retrieved from W3C: https://www.w3.org/TR/WCAG10/
1. ZaeffererJörn.*jQuery.validator.format() | jQuery Validtion Plugin* [Z].2013. Retrieved from jQuery Validtion Plugin | Form validation with jQuery: https://jqueryvalidation.org/jQuery.validator.format/
1. ZhangZhiling.*HarvestText* [Z].2022. Retrieved from GitHub: https://github.com/blmoistawinde/HarvestText


