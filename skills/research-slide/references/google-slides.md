# Google Slides：以原生稿与真实渲染为准

用户指定 Google Slides 时采用当前宿主支持的 Google 工作流；未指定而两种均可用时，可按其日常 Google Slides 习惯交付。已有稿修改与新建稿采用不同路径。不要把“请求编译成功”“PPTX 导出成功”或“本地 PNG 正常”写成 Google 原生渲染已通过。

## 已有 Google 稿：在副本与获准范围内续写

1. 用已连接且获准的工具读取当前 presentation、页序、pageSize、目标页原生对象和最新 revision，并取得实际页图。当前用户编辑后的原生稿是 source of truth。
2. 用户要求修改已有稿时，先保留可恢复的 snapshot/副本与源引用；只复制或修改获准页面。对照作者近邻页后，保留原对象的文字、表格、分组与格式，按需要使用 [inspect_slots.py](../scripts/inspect_slots.py) 查看槽位、[patch_slots.py](../scripts/patch_slots.py) 生成最小文字替换。它们只生成本地描述/请求，不提交。
3. 提交采用宿主支持的 revision 限制。revision 冲突时重新读取并检查用户改动，不覆盖新内容；重新定位精确 before/after 后再编译。避免 presentation 全局 replaceAllText 误改其他页面。
4. 在 Google 内回读最终页序与数据，检查 native table/shape/line 对象，再查看该原生稿实际渲染。发生结构调整时检查所有受影响页。没有在线渲染工具时，明确把 Google 视觉验收记为未验证。

Google batch 写入可附 `writeControl.requiredRevisionId`；当前源发生变化时必须重新读取。字段与行为以 [batchUpdate 参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/batchUpdate)为准。

## 新稿：优先使用宿主支持的导入或原生创作

- 宿主有支持的 Google 导入能力时，先生成已检查的可编辑 PPTX，再通过该路由导入；核对导入后的表格、公式、换行、字体、页脚与页序。导入前 PPTX 正常不能代替导入后验收。
- 宿主支持 native `batchUpdate` 时，可用下方离线编译器减少重复构造请求；先在获准的空白副本中创作，不向未知 presentation 提交。编译器不创建文件、不选账户、不改变 pageSize、不删除已有页。
- 若 Google connector 被管理员禁用，不能通过浏览器、直接 REST、临时凭据或另一个连接器绕过。继续完成可验证的本地 PPTX 和离线请求，把 Google 在线创建/导入/回读/渲染标为未执行；不能生成一个虚构 Google 链接。

## 离线原生请求编译器

```sh
python3 scripts/compile_google.py scene.json batch.json --manifest manifest.json --prefix run02
python3 scripts/test_compile_google.py
```

输入是 pt 坐标的 scene。`batch.json` 只包含可提交的 `requests`，可选 `--revision-id` 加入最新读取的 `requiredRevisionId`；`manifest.json` 独立记录逻辑 ID 到 Google ID 的映射、目标画幅与限制，不提交给 API。编译器只使用 Python 标准库，不访问网络、账户、图片 URL 或本地素材以外的服务，不发布素材。

```json
{
  "slideSizePt": [720,405],
  "slides": [{"id":"result-01","elements":[
    {"type":"text","x":28,"y":24,"w":660,"h":34,
     "text":"Quantization results","fontSize":24,"fontFamily":"Arial","bold":true},
    {"type":"table","x":28,"y":100,"w":500,"h":84,
     "values":[["Setting","Metric"],["Base","0.64"],["New","0.68"]],
     "colWidths":[320,180],"rowHeights":[28,28,28],"headerRows":1,
     "fontSize":14,"fontFamily":"Arial","fill":null}
  ]}]
}
```

### 接口的必要规则

- `type`: `text|rect|line|table|image`。除 line 外需要 `x,y,w,h`；所有几何和字号是 pt，原点在左上。未知字段、非有限值、负坐标、越出画幅、零尺寸、重复逻辑 id 均拒绝。新 slides 按顺序追加，elements 按从后到前叠放。
- 根 `slideSizePt` 默认 `[720,405]`，**仅是前置条件**。在线宿主须先读取目标 pageSize 并确认一致。每页 `id` 必须唯一；可选 `background` 默认白色；元素可选 `id` 在页内唯一。原生 Google IDs 从 prefix 和页/元素序号生成，须先检查不存在，避免重复提交。
- `text` 支持 `fontSize,fontFamily,color,bold,italic,underline,baselineOffset`，以及 `align:left|center|right|justify`、`verticalAlign:top|middle|bottom`、`lineSpacing` 百分比、`spaceAbove/spaceBelow` pt。默认 Arial 14pt、#333333、非粗体、100% 行距、段前后0。作者 profile 应显式覆盖这些默认值。
- `runs:[{text,bold?,italic?,fontSize?,fontFamily?,color?,underline?,baselineOffset?}]` 按序拼接；如同时提供 text 必须精确相同。样式范围按 UTF-16 计算，避免 emoji 后的加粗/颜色位置错位。支持换行；会被 Google 剥除的控制字符与 BMP 私有区字符直接拒绝。文字对象不自动缩字。Google 文本框自身内边距可能影响字面位置，需看原生页图。[文字索引与样式参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/text)
- `rect` 支持 `fill,lineColor,lineWidth`。颜色为 `RRGGBB` 或 `#RRGGBB`；fill 为 null、空字符串或 `none` 时输出 `NOT_RENDERED`，不误用黑色。lineColor 为空或 lineWidth 为0时无外框。[形状填充参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/shapes#ShapeBackgroundFill)
- `line` 使用 `x1,y1,x2,y2,color?,width?`，默认 #555555、.6pt。支持水平、竖直、斜向和反向直线；当前不支持绑定端点、箭头与虚线，不可暗示节点移动后会自动跟随。其非奇异仿射映射只完成离线端点数学检查，仍需 Google 实图验收。[线属性参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/lines)

Google 扩展的 underline、baselineOffset、spaceAbove/spaceBelow 与 PPTX 适配器的支持范围分别记录。PPTX 的 `image.path/alt`、table.padding、slide.notes 不在本 Google 编译器中；此处明确拒绝，宿主需通过原生上传/导入/notes 读取后写入等支持的路由处理，不得静默丢弃。

### 表格与图片的限制

`table.values` 是非空矩形二维数组，单元是字符串、有限数字或 null；null 表示空。需保持显示精度时传字符串。输出是真正的 `createTable` 与 native cellLocation 文本/格式，不用截图或矩形格冒充。合并单元格、span 和 cell 对象未实现，传入时明确报错。

`colWidths` 为每列 pt 数组，和等于 w；`rowHeights` 为每行 pt 数组，和等于 h。缺省均分。Google 原生列宽至少32pt；更窄的列编译时报错，不偷偷修改布局。rowHeights 以 **minRowHeight** 发给 Google，内容可能撑高行，实际 table bounds 必须在线回读。`headerRows` 仅指定前 N 行加粗，默认0，不自动涂色。`fill`、`lineColor`、`lineWidth` 设整表样式，默认白底、#999999边线、.5pt；表中文字默认10pt黑色居中；表格边线隐藏用透明 solidFill（其属性没有 propertyState）；`fills` 是同尺寸二维填充矩阵；`cellStyles` 是同尺寸的 null/样式对象矩阵，可覆盖文字、段落与 fill。优先级为整表 → header加粗 → cellStyles，填充为整表 → fills → cellStyles.fill。[表格属性参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations.pages/tables)，[请求与列宽规则](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#UpdateTableColumnPropertiesRequest)

`image` 只接受显式提供的 `url:https://...`。无 URL、本地 path、file/data URL 都报错；编译器绝不把私有图片上传或改成公开 URL。需要本地私有素材时使用宿主支持的上传/文件导入路由，或保留本地 PPTX。Google 的 URL 插图要求可公开访问，且会保留 source_url；交付前须确认用户授权、访问范围和素材来源。尺寸框按 Google 保持比例居中适配；此编译器不能离线验证图像实际尺寸、格式或可达性。[插图请求参考](https://developers.google.com/workspace/slides/api/reference/rest/v1/presentations/request#CreateImageRequest)

## 声明实际验证层级

离线测试覆盖：UTF-16 样式边界、native table 单元定位、列宽与行高请求、透明填充、直线端点变换、非法值与越界拒绝、不支持合并时显式失败、图片不隐式上传、revision guard、CLI失败不输出批次。测试通过只能写“离线编译与行为测试通过”。只有获准在 Google 创建/导入、回读并逐页查看实际渲染后，才能写“Google 原生渲染已检查”。Google 与 PPTX 的可编辑性、视觉、字体兼容性分别记录；任何未做项目保持未验证。
