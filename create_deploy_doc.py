# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'C:/Windows/Fonts/msyh.ttc'))

# 桌面路径
desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
output_path = os.path.join(desktop, 'CET6项目阿里云部署问题排查记录.pdf')

doc = SimpleDocTemplate(output_path, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=2*cm, bottomMargin=2*cm)

# 样式定义
styles = {
    'title': ParagraphStyle('title', fontName='MicrosoftYaHei', fontSize=18,
                            leading=28, alignment=1, spaceAfter=20,
                            textColor=HexColor('#1a1a2e')),
    'h1': ParagraphStyle('h1', fontName='MicrosoftYaHei', fontSize=14,
                         leading=22, spaceBefore=16, spaceAfter=10,
                         textColor=HexColor('#16213e'),
                         borderWidth=0, borderPadding=0),
    'h2': ParagraphStyle('h2', fontName='MicrosoftYaHei', fontSize=12,
                         leading=18, spaceBefore=12, spaceAfter=8,
                         textColor=HexColor('#0f3460')),
    'body': ParagraphStyle('body', fontName='MicrosoftYaHei', fontSize=10,
                           leading=18, spaceAfter=6,
                           textColor=HexColor('#333333')),
    'code': ParagraphStyle('code', fontName='MicrosoftYaHei', fontSize=9,
                           leading=14, spaceAfter=8, leftIndent=20,
                           backColor=HexColor('#f5f5f5'),
                           borderWidth=0.5, borderColor=HexColor('#ddd'),
                           borderPadding=6, textColor=HexColor('#c7254e')),
    'success': ParagraphStyle('success', fontName='MicrosoftYaHei', fontSize=10,
                              leading=16, spaceAfter=6, leftIndent=10,
                              borderWidth=0, borderPadding=4,
                              textColor=HexColor('#155724')),
    'error': ParagraphStyle('error', fontName='MicrosoftYaHei', fontSize=10,
                            leading=16, spaceAfter=6, leftIndent=10,
                            borderWidth=0, borderPadding=4,
                            textColor=HexColor('#721c24')),
}

story = []

# 标题
story.append(Paragraph('CET-6 词汇学习平台', styles['title']))
story.append(Paragraph('阿里云服务器部署问题排查记录', styles['title']))
story.append(Spacer(1, 10))
story.append(Paragraph('日期: 2026年5月24日 | 服务器: 8.160.188.108', styles['body']))
story.append(Spacer(1, 20))

# 项目概述
story.append(Paragraph('一、项目概述', styles['h1']))
story.append(Paragraph('CET-6 六级词汇学习平台是一个 Web 应用，支持单词浏览、搜索、随机抽词、拼写检测、AI 造句检测等功能。', styles['body']))
story.append(Paragraph('技术栈: Python FastAPI + Vue 3 + Vite + MySQL/MariaDB + Nginx', styles['body']))

# 问题列表表格
story.append(Spacer(1, 10))
data = [
    ['序号', '问题', '原因', '解决方案'],
    ['1', '站点未找到', 'Nginx 未配置站点', '宝塔面板添加 HTML 站点'],
    ['2', '500 Internal Server Error', 'Nginx 无权限访问目录', 'chmod -R 755'],
    ['3', 'MariaDB 启动失败', '配置文件有无效参数', '删除 early-plugin-load'],
    ['4', '数据库连接拒绝', 'socket 文件路径不对', '改用 127.0.0.1 TCP 连接'],
    ['5', '数据库密码错误', '密码未正确设置', 'skip-grant-tables 重置'],
    ['6', '数据库不存在', 'cet6zx 未创建', 'CREATE DATABASE + 导入'],
    ['7', 'SQL 导入失败', '排序规则不兼容', '替换 utf8mb4_0900_ai_ci'],
]
t = Table(data, colWidths=[1.2*cm, 4*cm, 4.5*cm, 5.5*cm])
t.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftYaHei'),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4a00e0')),
    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9fa'), HexColor('#ffffff')]),
    ('TOPPADDING', (0, 0), (-1, -1), 6),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
]))
story.append(t)

# 详细排查过程
story.append(PageBreak())
story.append(Paragraph('二、详细排查过程', styles['h1']))

# 问题1
story.append(Paragraph('问题1: 访问 http://8.160.188.108 显示"没有找到站点"', styles['h2']))
story.append(Paragraph('错误信息: 您的请求在Web服务器中没有找到对应的站点!', styles['error']))
story.append(Paragraph('原因分析: 宝塔 Nginx 没有配置对应的站点，需要添加站点配置。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph('1. 登录宝塔面板 (http://8.160.188.108:8888)', styles['body']))
story.append(Paragraph('2. 点击「网站」->「添加站点」', styles['body']))
story.append(Paragraph('3. 选择「HTML项目」，域名填 8.160.188.108', styles['body']))
story.append(Paragraph('4. 根目录填 /home/admin/project2/backend/frontend/dist', styles['body']))
story.append(Paragraph('5. 在站点配置中添加 API 反向代理:', styles['body']))
story.append(Paragraph('location /api/ {<br/>    proxy_pass http://127.0.0.1:8000;<br/>    proxy_set_header Host $host;<br/>    proxy_set_header X-Real-IP $remote_addr;<br/>}', styles['code']))
story.append(Paragraph('结果: 站点可以访问，但出现 500 错误', styles['success']))

# 问题2
story.append(Paragraph('问题2: 500 Internal Server Error', styles['h2']))
story.append(Paragraph('错误日志: stat() "/home/admin/project2/backend/frontend/dist/index.html" failed (13: Permission denied)', styles['error']))
story.append(Paragraph('原因分析: Nginx 工作进程 (www 用户) 没有权限访问 /home/admin/ 目录。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph('chmod -R 755 /home/admin', styles['code']))
story.append(Paragraph('nginx -s reload', styles['code']))
story.append(Paragraph('结果: 前端页面可以正常显示', styles['success']))

# 问题3
story.append(Paragraph('问题3: MariaDB 启动失败', styles['h2']))
story.append(Paragraph('错误日志: /usr/libexec/mysqld: unknown variable \'early-plugin-load\'', styles['error']))
story.append(Paragraph('原因分析: /etc/my.cnf 中有 MySQL 特有的参数 early-plugin-load，MariaDB 不支持。另外 max_allowed_packet = 100G 过大。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph('cp /etc/my.cnf /etc/my.cnf.bak', styles['code']))
story.append(Paragraph("sed -i '/early-plugin-load/d' /etc/my.cnf", styles['code']))
story.append(Paragraph("sed -i 's/max_allowed_packet = 100G/max_allowed_packet = 100M/' /etc/my.cnf", styles['code']))
story.append(Paragraph('systemctl start mariadb', styles['code']))
story.append(Paragraph('结果: MariaDB 成功启动', styles['success']))

# 问题4
story.append(Paragraph('问题4: 数据库连接拒绝 (socket 问题)', styles['h2']))
story.append(Paragraph('错误信息: Can\'t connect to MySQL server on \'localhost\' ([Errno 111] Connection refused)', styles['error']))
story.append(Paragraph('原因分析: 配置文件中 socket = /tmp/mysql.sock，但实际 socket 文件在 /var/lib/mysql/mysql.sock。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph('修改 /home/admin/project2/backend/database.py', styles['body']))
story.append(Paragraph('"host": "localhost"  ->  "host": "127.0.0.1"', styles['code']))
story.append(Paragraph('结果: 使用 TCP 连接代替 socket 连接', styles['success']))

# 问题5
story.append(Paragraph('问题5: 数据库密码错误', styles['h2']))
story.append(Paragraph('错误信息: Access denied for user \'root\'@\'localhost\' (using password: YES)', styles['error']))
story.append(Paragraph('原因分析: MariaDB root 密码未正确设置或与配置文件中不一致。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph("1. 在 /etc/my.cnf 末尾添加 skip-grant-tables", styles['body']))
story.append(Paragraph("2. 重启 MariaDB: systemctl restart mariadb", styles['body']))
story.append(Paragraph("3. 连接数据库: mysql -u root -h 127.0.0.1", styles['body']))
story.append(Paragraph("4. 执行 SQL:", styles['body']))
story.append(Paragraph("FLUSH PRIVILEGES;<br/>ALTER USER 'root'@'localhost' IDENTIFIED BY 'QQ2763449353';<br/>FLUSH PRIVILEGES;", styles['code']))
story.append(Paragraph("5. 删除 skip-grant-tables 并重启", styles['body']))
story.append(Paragraph('结果: 密码重置成功', styles['success']))

# 问题6
story.append(Paragraph('问题6: cet6zx 数据库不存在', styles['h2']))
story.append(Paragraph('错误信息: Unknown database \'cet6zx\'', styles['error']))
story.append(Paragraph('原因分析: 切换到 MariaDB 后，之前的数据库未迁移。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph("mysql -u root -pQQ2763449353 -h 127.0.0.1 -e \"CREATE DATABASE cet6zx CHARACTER SET utf8mb3;\"", styles['code']))
story.append(Paragraph("mysql -u root -pQQ2763449353 -h 127.0.0.1 cet6zx < migration.sql", styles['code']))
story.append(Paragraph('结果: 数据库和表结构创建成功', styles['success']))

# 问题7
story.append(Paragraph('问题7: SQL 导入失败 (排序规则不兼容)', styles['h2']))
story.append(Paragraph('错误信息: ERROR 1273 (HY000): Unknown collation: \'utf8mb4_0900_ai_ci\'', styles['error']))
story.append(Paragraph('原因分析: cet6zx.sql 是从 MySQL 8.0 导出的，使用了 utf8mb4_0900_ai_ci 排序规则，MariaDB 10.5 不支持。', styles['body']))
story.append(Paragraph('解决方案:', styles['body']))
story.append(Paragraph("sed -i 's/utf8mb4_0900_ai_ci/utf8mb4_general_ci/g' /home/admin/project2/backend/cet6zx.sql", styles['code']))
story.append(Paragraph("mysql -u root -pQQ2763449353 -h 127.0.0.1 cet6zx < cet6zx.sql", styles['code']))
story.append(Paragraph('结果: 5523 条单词数据成功导入', styles['success']))

# 总结
story.append(PageBreak())
story.append(Paragraph('三、最终配置总结', styles['h1']))

config_data = [
    ['配置项', '值'],
    ['服务器 IP', '8.160.188.108'],
    ['Nginx 站点根目录', '/home/admin/project2/backend/frontend/dist'],
    ['后端入口', 'http://127.0.0.1:8000'],
    ['数据库类型', 'MariaDB 10.5'],
    ['数据库主机', '127.0.0.1:3306'],
    ['数据库名', 'cet6zx'],
    ['数据库用户', 'root'],
    ['前端框架', 'Vue 3 + Vite'],
    ['后端框架', 'Python FastAPI'],
    ['单词数量', '5523 条'],
]
t2 = Table(config_data, colWidths=[4*cm, 11*cm])
t2.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'MicrosoftYaHei'),
    ('FONTSIZE', (0, 0), (-1, -1), 10),
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4a00e0')),
    ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
    ('BACKGROUND', (0, 1), (0, -1), HexColor('#f0e6ff')),
    ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
]))
story.append(t2)

story.append(Spacer(1, 20))
story.append(Paragraph('四、经验教训', styles['h1']))
story.append(Paragraph('1. MySQL 和 MariaDB 配置不完全兼容，注意排序规则和特有参数的差异。', styles['body']))
story.append(Paragraph('2. 宝塔面板的 MySQL 和系统 MariaDB 可能共存，需注意端口和 socket 冲突。', styles['body']))
story.append(Paragraph('3. Nginx 代理后端时，建议使用 127.0.0.1 而非 localhost，避免 socket 连接问题。', styles['body']))
story.append(Paragraph('4. 部署前检查文件权限，确保 Nginx 用户有权限访问静态资源目录。', styles['body']))
story.append(Paragraph('5. MariaDB 密码重置可通过在 my.cnf 添加 skip-grant-tables 实现。', styles['body']))

# 构建 PDF
doc.build(story)
print(f'PDF 已生成: {output_path}')
