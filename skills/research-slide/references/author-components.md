# 可编辑科研表格与逐位置机制图

当作者页需要两层分组表头、纵向合并的模型/设置列，或需要按同一通道逐行追踪输入到输出时，使用 `scripts/author_components.mjs`。新页面的原始品牌素材和原生 bullet 列表也由同模块提供。这是原生制作组件，不是自动选择内容、推断结论或绘制任意装饰的模板。它补足基础 scene adapter 故意不处理的合并表头与科研向量机制。

模块依赖当前宿主的 `@oai/artifact-tool`，通过该包的依赖解析取得 `skia-canvas`，加载随 skill 提供的**完整** `FrankRuhlLibre-variable.ttf` 与 `Montserrat-variable.ttf`，分别以 `Frank Ruhl Libre` 和 `Montserrat` 注册。不要使用 PDF 子集或仅有部分字形的字体替代；字体缺失时会明确报错。Montserrat 正体可变字体来自 [Google Fonts 官方源](https://github.com/google/fonts/tree/main/ofl/montserrat)，支持100–900字重，随附 `Montserrat-OFL.txt` 保留其 SIL Open Font License 1.1。开发时在工作副本的 scripts 旁连接宿主 node_modules；分发包中排除该机器路径与 node_modules。

所有输入坐标、宽高、字号、行高、边线宽度均为 **pt**，模块内部统一乘4/3转为 Artifact Tool 的 px。函数接收一个宿主已创建的 slide，不创建额外封面、标题、说明或备份页。

```js
import {addGroupedTable, addVectorPipeline, addAuthorChrome, addAuthorBullets, authorText, addFooter}
  from '/absolute/skill/path/scripts/author_components.mjs';
```

## addGroupedTable(slide, config)

```js
const {table, mergeRanges, bodyRowOffset} = addGroupedTable(slide, {
  x:28, y:80, w:664, h:132,
  columns:['Model','Setting','Error A','Error B','Task A','Task B'],
  groups:[
    {label:'Reconstruction', start:2, end:3},
    {label:'Task quality', start:4, end:5}
  ],
  rows:[
    ['A','Base','0.00420','0.03100','64.20','71.80'],
    ['A','Variant','0.00385','0.02950','64.90','72.10'],
    ['B','Base','0.00600','0.04150','63.10','70.50'],
    ['B','Variant','0.00570','0.03980','63.60','70.90']
  ],
  colWidths:[92,110,104,104,127,127],
  rowHeights:[22,22,22,22,22,22],
  merges:[
    {startRow:0,endRow:1,startColumn:0,endColumn:0},
    {startRow:2,endRow:3,startColumn:0,endColumn:0}
  ],
  cellStyles:{'3,2':{color:'#CC0000',bold:true},'3,4':{color:'#0000CC',bold:true}}
});
```

这些是独立构造的示意值，不能作为实验结果复用。

- 必填 `x,y,w,h,columns,rows`；rows 只含 body，不含表头。字符串按原样保留，数字才转为字符串；显示精度需要 `"0.00420"` 这类字符串。null 为空格，布尔、对象、非有限数拒绝。
- 始终有两行表头。`groups` 的 start/end 是**包含端点**的0起列索引，分组不能重叠。分组标签在第一行合并；分组覆盖的列在第二行显示 columns 标签。没有被 group 覆盖的列将两行表头纵向合并，因此 Model/Setting 等 stub 不出现一个多余的空顶格。
- `merges` 的行索引针对 **body**，0是第一个数据行；列索引针对整表。函数会给行加2后调用宿主的 `table.merge({startRow,endRow,startColumn,endColumn})`。合并区只允许重复同一字符串或空值；如果会丢掉不同数值就拒绝。不会把不同数据拼成一个大单元格。重叠及越界合并拒绝。
- `cellStyles` 使用**完整表格坐标**，包含第0、1两行表头。可传 `{ 'row,column': style }`，或与完整表尺寸一致的二维 null/style 数组。body第1行、Error A列对应 `'3,2'`。style 可设 `fontSize,fontFamily,color,bold,italic,align,verticalAlign,fill,lineSpacing`。
- `colWidths` 是 pt 数组、和等于w；`rowHeights` 含两行表头、和等于h。缺省均分。PPTX 组件允许科学上合适的窄列；Google REST scene compiler 的32pt最小列宽是其后端限制，不迁移为 PPTX 的限制。
- 缺省 `fontSize:9.5`、`fontFamily:'Arial'`、黑色、居中、竖直居中；表头 `headerFill:'#CCCCCC'`、`headerBold:true`；body白色；`gridColor:'#333333'`、`gridWidth:.5`、`padding:1`。可覆盖这些值，或以作者近邻页的实际样式为准。不会自动推断赢家、全行加色或选取极值。
- 表头可换行；body没有自动缩字。若窄列或行高容不下文本，应由制作者改宽高、保留必要字段并重新渲染。组件不暗中删字、截断或降低字号。
- 返回 `table` 原生对象，以及 `headerRows:2,bodyRowOffset:2,values,mergeRanges,colWidths,rowHeights`；可继续进行宿主原生编辑。

## addVectorPipeline(slide, config)

```js
const pipeline = addVectorPipeline(slide, {
  x:28, y:240, w:664,
  labelWidth:160, rowHeight:18, gap:16, fontSize:10.5,
  stages:[
    {label:'Input', values:['-3.00','-2.00','-1.00','0.00','0.00','1.00','2.00','3.00']},
    {label:'Encoded index', values:['0','1','2','3','3','4','5','6'],
     formula:'C = [-4, -2, -1, 0, 1, 2, 4]; equal distances choose away from zero'},
    {label:'Reconstruction', values:['-4.00','-2.00','-1.00','0.00','0.00','1.00','2.00','4.00']},
    {label:'Absolute error', values:['1.00','0.00','0.00','0.00','0.00','0.00','0.00','1.00'],
     formula:'Mean absolute error = (1 + 1) / 8 = 0.25'}
  ]
});
```

- 必填 `x,y,w,stages`，每个 stage 有 label 和 **字符串** values。所有阶段通道数必须相同，每列对应的通道位置保持一致。不同数目的数组不能伪装成共享通道。
- 每个 stage 生成一张真实的一行表格，左边为可编辑 label，阶段之间是原生竖直箭头。默认 `labelWidth:130,rowHeight:20,gap:18,fontSize:11`；可选 `colWidths` 只针对向量区域，和等于 `w-labelWidth`，否则等分。
- `formula` 是放在该行下方 gap 中的可编辑普通文字，不是原生数学对象。简单等式可用；分式、复杂上下标、求和边界等应使用宿主准确的 rich math/OMML/原生公式路径，不能用难读的线性文本代替。配置可选 formulaFontSize、formulaHeight、formulaFontFamily。
- stage 可提供 `cellStyles:[style,...]`、`fill`、`bold`；也可设整图的 gridColor/gridWidth/textColor/fontFamily/padding/arrowColor/arrowWidth。颜色表示哪个通道、状态或误差需由研究输入确定。
- stage 的 `connectToNext:false` 不画该阶段到下一阶段的箭头；缺省true。并列的 companion/reference 输入不自动构成计算变换，只有真实计算关系才连箭头。通用参数不含任何测试题特例。
- 这些箭头是原生但**未绑定表格端点**，手动移动表格后需要同步调整，不能声称箭头自动跟随。若要附着、分支或更复杂计算路径，使用宿主 connector API 与可绑定的形状。
- 返回 `tables,labels,formulas,arrows,channelCount,vectorX,vectorWidth,boundsPt`。调用者检查 boundsPt 与脚注/下一内容的间距；科学运算和数值来自调用者，组件不会计算或修正实验。

## addAuthorChrome(slide, config)

```js
const chrome = addAuthorChrome(slide, {family:'sai', pageNumber:12});
// NYU family must likewise be explicit: {family:'nyu', pageNumber:12}
// Existing source already has chrome: preserve it and skip insertion.
addAuthorChrome(slide, {family:'nyu', pageNumber:12, existingChrome:true});
```

- `family` **必须显式**为 `sai` 或 `nyu`；不按内容、主题或作者身份猜测。只适用于720×405pt画幅的新建页；已有原生模板保留实际 chrome，不重复插入。
- 默认顶部原始 strip 位于 `[0,0,720,20]`；NYU logo框为 `[31,357,63,23]`；SAI logo框为 `[5,353,106,26]`。引用 skill 内的原始素材文件，以非空 bytes 嵌入，不重画、截图替代、裁切或变形。MIME按图像 payload 判断，`fit:'contain'` 保持原始比例，框可能有少量空白。
- 页码默认 `[674,362,13.5,10]`、Montserrat **Bold 7pt**、紫色#330662、右对齐，字体/字重/字号/颜色依据非目标例稿的 `Montserrat-Bold` 实测；未给 pageNumber 就不造页码。可用 `pageFontFamily/pageBold/pageFontSize/pageColor` 覆盖其他真实原稿样式，`pageBold:false` 会保留普通字重。几何框按多个训练页的右对齐锚点校准，不能把字形测量框直接当文本框。PPTX 保存原生可编辑文本及字体/粗体/颜色属性；宿主回读渲染通过上述完整字体注册，不代表接收方已安装或嵌入该字体，也不代表 PowerPoint/Google 在线渲染已验证。
- 共享品牌数据在 `assets/author-profile/chrome.json`（version1，pt）；helper直接读取它。`canvasPt`、`pageMarker.geometry/fontFamily/fontSizePt/color/bold/align` 定义公共画幅与页码；`families.nyu/sai.asset/logoGeometry/topStrip/occupiedRegions` 定义各品牌原始素材、contain框和保留区。`asset`均是该profile目录内的相对文件名。stage packet只复制当前输入明确指定品牌的原始logo与共享strip；科学结构例页不能替换canonical identity facts中的品牌/页码。
- 训练页存在两组固定右端锚点：examples01/02/05/08/11的字形右端约687.17pt；03/04/06/07/09/10约684.34pt，纵向均约362.38–370.91pt。默认对应前者；后者可显式用 `variant:'marker-left-3pt'`（文本框 `[671,362,13.5,10]`），或按实际源页覆盖 `pageMarker`。该变体跨多个训练页，不按NYU/SAI自动推断，也不能把example10的局部偏移应用到所有NYU页。显式几何与字体参数仍优先，未给页码时仍不创建页码。
- `topStrip`、`logo`、`pageMarker` 可为false以关闭，或 `{x,y,w,h}` 覆盖真实模板几何。不改变原始品牌素材。新建页只调用一次；同一 live slide 再次调用、或原生页已有本组件标记过的素材，会跳过。对其他来源的已有模板，制作者必须先检查其实际页图，并用 `existingChrome:true` 保留；该参数不是自动识别任意旧 logo 的声明。
- 返回 `objects,images,pageMarker,skipped,occupiedFooterRegions,occupiedTopRegions`（跳过已有稿时返回可用的请求区域）；footer regions 为保守的完整对象框，用于检查正文、表格、日志和机制图是否侵犯页脚。现有稿若几何不同，传入已读取的实际框，不能把默认框当成观测。

v8 的独立原生烟测从最终保存PPTX重新import后渲染：492的显式左移变体与训练example10的ink边界同为 `[1343,728,1367,737]`；662默认与训练example11同右端1373px、纵向728–737px，左端仅相差1px；两位12与一位9保持同一右端1373px。XML确认文本框pt几何、Montserrat Bold7/#330662与右对齐，显式Arial普通8pt/颜色/几何覆盖有效，原始两种logo/strip payload字节一致，native bullet仍有Arial buFont。7页通过相同三字体design policy的宿主finalizer（0 findings/0 warnings），并逐页查看保存后回读PNG。比较使用训练PDF/Fitz2x与宿主Artifact1.5x，均1440×810px；这证明锚点修正，不声称光栅器完全相同或PowerPoint/Google在线验证。

## addAuthorBullets(slide, config)

```js
const list = addAuthorBullets(slide, {
  x:35.5,y:89,w:650,h:120,fontSize:14,lineSpacing:115,spaceAfter:0,
  items:[
    {level:0,runs:[{text:'Observation: ',bold:true},{text:'keep the original uncertainty.'}]},
    {level:1,text:'Compare the same channel under the same conditions.'},
    {level:2,runs:[{text:'Precision: ',bold:true},{text:'preserve 0.00420 exactly.'}]}
  ]
});
```

- 返回一整个**原生可编辑文本框**，每个 item 是真正的 paragraph，使用 native bullet 元数据；不把 bullet 字符加进正文，不用独立小圆点/文本框伪装列表。复杂公式按原生数学工作流插入，不编造拼写错误模仿作者。
- item 有 text 或 runs、level0/1/2（缺省0）。runs 的 text 顺序保持，支持句首加粗后接普通文字，不把全段误加粗。可以覆盖 item/run 的 fontSize/fontFamily/color/bold/italic。每个 item 是一个段落；需要新段落就另列 item，不在字符串中塞换行。长文字由同一文本框自然折行，不自动缩字。
- 默认 Arial14pt、#333333、lineSpacing100%（可在item覆盖）、spaceAfter0pt；item 可覆盖 spaceAfter/spaceBefore。所有对外字号与段距都是pt，**lineSpacing是百分比**。
- 默认左边距36pt、hanging27pt，每升一级额外缩进36pt；可设 `marginLeftPt,hangingPt,levelIndentPt`，item可覆盖前两项。本作者实测前两级是 `●/○`（U+25CF/U+25CB），不是常见小圆点 `•/◦`。默认第三级为 `■`，只有需要第三级时才按实际参照确认/覆盖；可用三元素 `bulletCharacters` 覆盖。宽悬挂缩进让大圆与正文分开，续行仍对齐正文。不要为了避免调整缩进而改成小圆点。改变字体/字号后仍需看实际续行位置。runtime example07 的原稿正文行基线间距19.32pt（14pt、115%）；example09为16.8pt（14pt、100%）。不要用每段后追加6–8pt替代连续列表的实际行距。
- 编译严格区分单位：paragraph的marginLeft/indent为EMU（×12700），spaceBefore/After为百分之一pt（×100），lineSpacingPercent为百分之一千的百分比（100%→100000）。native paragraph level另设0/1/2；shape几何仍仅×4/3。该运行时设置显式paragraphStyle时也须保留其中的bulletCharacter，否则导出可能变buNone；当前实现已同时保留并做XML回归。
- 同时通过宿主支持的 `paragraphStyle.bulletTypeface` 显式指定原生 bullet 字体，默认 Arial，跟随 item 或列表的 `fontFamily`，也可用 item/列表的 `bulletFontFamily` 单独覆盖（item优先）；导出的 `a:buFont` 保留字体选择，避免仅有 `buChar` 时转换器自行改用 OpenSymbol。不设置与显式字体冲突的 followsText 标记。仍是 native bullet 元数据，符号、层级和缩进不变，不把字符打进正文或导出后改 XML。
- Google 原生对应路径是宿主 `createParagraphBullets` 与 `updateParagraphStyle`，必要时通过前导tabs确定层级；该请求移除tabs、会改变后续UTF-16索引，所以先处理bullets再回读/定位run样式，不沿用旧索引。[官方请求说明](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#CreateParagraphBulletsRequest)。优先使用宿主支持的PPTX原生导入并检查结果；当前基础Google scene compiler不自动支持此helper的native列表，不能静默转成手打符号。

## authorText 与 addFooter

当前宿主回读PPTX不会恢复图像的alt标记，因此不能依赖图像标记自动识别回读页已有chrome。续写现有模板时先检查实际页图，显式传`existingChrome:true`或不调用该插入函数；同一live slide的重复调用仍由WeakMap去重。不要把这项能力写成回读后自动识别保证。

`authorText(slide,{x,y,w,h,text,...})` 添加原生文本框，支持普通 text 或 runs，字号默认14pt，文本不自动缩小。`runs:[{text,bold?,italic?,fontFamily?,fontSize?,color?}]` 用于句内强调，内容顺序保持不变。复杂数学仍走宿主公式路径。

`addFooter(slide,{pageNumber,text?,x?,y?,w?,h?,fontSize?,color?})` 默认左28pt、上365pt、宽660pt、紫色#57068C，页码在右端约688pt。该默认属于本私有作者系列；存在邻页时按实际页脚位置覆盖。函数不会插入徽标，调用者选择确实属于该系列的品牌原始素材，不能用示意 logo。它不自动探测页面尺寸。

## 验证与跨后端交付

可编辑的 [generic 例稿](../assets/author-components-demo/example.pptx) 与 [保存后回读预览](../assets/author-components-demo/example.png) 随包提供，只演示 API，不作为整页作者版式的优先依据。例稿实际生成：一张6列、两级表头、纵向 stub 合并和选择性红蓝文字的表，加四张8通道单行表。导出包检查使用真正的 `a:tbl`、`gridSpan`、`rowSpan`；数值显示精度及零图片检查通过。该示例不来自测试目标，也不证明特定科研内容或作者盲评通过。

交付 PPTX 前按当前宿主 finalization 检查，重新读取保存后的 PPTX，逐页检查实际图和可编辑性。该组件的 preview 不能代替最终保存文件回读。

Google Slides 优先使用宿主支持的 PPTX原生导入，再检查其真实渲染与合并表格结构。宿主允许 native batchUpdate 时，也可用 Google createTable、insertText、样式与 **mergeTableCells** 构建同等结构；Google 请求形如 `{mergeTableCells:{objectId,tableRange:{location:{rowIndex,columnIndex},rowSpan,columnSpan}}}`；这与本组件含端点的 end 索引不同。提交前让合并覆盖区只有锚点单元保留所需文本，其余覆盖单元为空；Google 会把被合并单元的文字拼接到锚点，重复模型名不能直接整区合并。见 [官方请求参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#MergeTableCellsRequest)。基础 `compile_google.py` 目前明确拒绝合并，不能把本组件场景直接塞进去然后宣称等价。只有在线导入/构建、回读与实图检查过才能报告 Google 通过；本次组件示例没有 Google 在线验证。


### Chrome、bullet 与关系箭头的实测

随包的两页 bullet/chrome 独立示例分别用SAI与NYU原始素材：每页嵌入两张非空payload图，列表为native pPr/buChar，levels为0/1/2/0；marL分别228600/457200/685800/228600、hanging为-114300，6pt段后距输出600，100%行距输出100000。句首粗体run的b=1，后续普通run的b=0。四阶段向量把第一条关系明确关闭，只输出两个native箭头，字符串-3.00/-4.00/0.00/4.00原样保留。

检查了缺少family时报错、既有chrome跳过、重复调用不重复插图、非法bullet level在落对象前拒绝。本次两页例稿已通过宿主finalizer（包完整性、bullet geometry、字体策略、native table owner与重新导入均通过，0 findings、0 warnings），并已从最终保存PPTX重新import、渲染并逐页查看全尺寸PNG。完整的XML检查与finalizer原始记录随配套评测包保留。该generic示例不使用benchmark、目标页或评审意见，也不代表Google在线渲染通过。

原生 bullet 与两种品牌 chrome 的 [可编辑烟测稿](../assets/author-components-demo/bullets-chrome.pptx)、[SAI回读](../assets/author-components-demo/bullets-chrome-sai.png) 和 [NYU回读](../assets/author-components-demo/bullets-chrome-nyu.png) 随包附带，仅演示组件，不替代作者功能例页。

### v6 的组件默认修正

上面的 v4 烟测文件作为历史记录保留，其显式6pt段距和旧符号不再代表本作者默认。当前组件依据非目标例页的真实字符/坐标，改为●/○、36pt左边距、27pt悬挂、36pt层级增量、0pt段后距。100%行距仍是通用缺省，runtime example07 由调用者显式设115%。这次修正来自测量，不是模仿目标页的排版缺陷。
