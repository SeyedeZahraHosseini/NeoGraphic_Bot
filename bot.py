import telebot
from PIL import Image, ImageDraw, ImageFont
import db
from db import Cursor
import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO
from datetime import datetime
import random
import os
from moviepy import *


global back_color
telebot.apihelper.API_URL = "https://tapi.bale.ai/bot{0}/{1}"
bot = telebot.TeleBot(os.environ['TOKEN'],threaded=False)


# region main_menu

# main menu
@bot.message_handler(commands=['start'])
def start_method(message):
    Cursor.execute(
        "SELECT * FROM users WHERE chat_id = ?",
        (message.chat.id,)
    )
    result=Cursor.fetchone()

    if not result:
        Cursor.execute("""
            INSERT INTO users
            (chat_id, username, first_name, state, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message.chat.id,
            message.chat.username,
            message.chat.first_name,
            'start',
            datetime.now()
        ))
    db.MAIN_DB.commit()

    markup=telebot.types.InlineKeyboardMarkup()
    settings_btn=telebot.types.InlineKeyboardButton('تنظیمات ⚙',callback_data='settings')
    photo_btn=telebot.types.InlineKeyboardButton('تولید پست متنی 🖼',callback_data='photo')
    video_btn=telebot.types.InlineKeyboardButton('تولید ویدیو متنی 🎥',callback_data='video')

    markup.add(photo_btn,video_btn,settings_btn,row_width=1)

    bot.send_message(message.chat.id,'سلام 👋\n من نئوگرافیک هستم، دستیار شخصی شما🎨',reply_markup=markup)

# endregion


# region call_back_query

@bot.callback_query_handler(func=lambda call: True)
def call_back(call):
    if call.data=='settings':
        settings_method(call)
    elif call.data=='photo':
        Cursor.execute(
        "UPDATE users SET state = ? WHERE chat_id = ?",
        ('photo', call.message.chat.id)
        )
        db.MAIN_DB.commit()

        bot.send_message(call.message.chat.id,'متنی که می خوای روی تصویر باشه رو برام بفرست \n الان جادوی نئو رو میبینی ✨')   
        
    elif call.data=='video':
        Cursor.execute(
        "UPDATE users SET state = ? WHERE chat_id = ?",
        ('video', call.message.chat.id)
        )
        db.MAIN_DB.commit()

        bot.send_message(call.message.chat.id,'متنی که می خوای روی ویدیو باشه رو برام بفرست \n الان جادوی نئو رو میبینی ✨')
       
    elif call.data=='color':
        choose_color(call)
    elif call.data=='font':
        choose_font(call)
    elif call.data=='back_ground':
        choose_background(call)
    elif 'rang' in call.data:
        set_color(call)
    elif call.data=='settings_menu':
        settings_method(call)
    elif call.data=='main_menu':
        start_method(call.message)
    elif 'font' in call.data:
        set_font(call)
    elif 'back_' in call.data:
        set_background(call)
  
# endregion

# test_handler
@bot.message_handler(content_types=['text'])
def handle_text(message):
    Cursor.execute(
        "SELECT state FROM users WHERE chat_id = ?",
        (message.chat.id,)
    )

    result = Cursor.fetchone()
    if not result:
        return

    state = result[0]
    if state=='photo':
        bot.send_message(message.chat.id,'گر صبر کنی ز غوره حلوا سازم...')
        my_text=message.text
        generate_img(my_text,message,mode="post")

    elif state=='video':
        bot.send_message(message.chat.id,'گر صبر کنی ز غوره حلوا سازم...')
        my_text=message.text
        result=generate_img(my_text,message,mode="video")
        make_video(message,result)
        




# region settings_menu
# منو تنظیمات
def settings_method(call):

    markup=telebot.types.InlineKeyboardMarkup()
    color_btn=telebot.types.InlineKeyboardButton('رنگ بکگراند 🎨',callback_data='color')
    font_btn=telebot.types.InlineKeyboardButton('فونت ✒',callback_data='font')
    background_btn=telebot.types.InlineKeyboardButton('انتخاب بکگراند 🌄',callback_data='back_ground')
    markup.add(color_btn,font_btn,background_btn,row_width=1)

    bot.send_message(call.message.chat.id,'اینجا میتونی تولیدات خودت رو شخصی سازی کنی 💎',reply_markup=markup)

# endregion

# region color

# منو رنگ
def choose_color(call):

    markup=telebot.types.InlineKeyboardMarkup()
    black_btn=telebot.types.InlineKeyboardButton('مشکی',callback_data='rang_black')
    white_btn=telebot.types.InlineKeyboardButton('زیتونی',callback_data='rang_green')
    green_btn=telebot.types.InlineKeyboardButton('آبی دودی',callback_data='rang_blue')
    blue_btn=telebot.types.InlineKeyboardButton('زرشکی ',callback_data='rang_red')
    red_btn=telebot.types.InlineKeyboardButton('خاکی',callback_data='rang_brown')
    red_btn=telebot.types.InlineKeyboardButton('کاراملی',callback_data='rang_karameli')

    markup.add(black_btn,white_btn,green_btn,blue_btn,red_btn,row_width=2)
    bot.send_message(call.message.chat.id,'رنگ مدنظرت رو انتخاب کن 🎨',reply_markup=markup)

# تنظیم رنگ
def set_color(call):

    markup=telebot.types.InlineKeyboardMarkup()
    settings_menuBtn=telebot.types.InlineKeyboardButton('منو تنظیمات ⚙',callback_data='settings_menu')
    main_menuBtn=telebot.types.InlineKeyboardButton('منو اصلی 🏠',callback_data='main_menu')
    markup.add(settings_menuBtn,main_menuBtn,row_width=1)

    color=call.data
    back_color=None
    match color:
        case 'rang_black':
            back_color="#111111"
        case 'rang_brown':
            back_color="#3D392E"
        case 'rang_green':
            back_color="#55552F"
        case 'rang_blue':
            back_color="#3A4656"
        case 'rang_red':
            back_color="#670001"
        case 'rang_karameli':
            back_color="#866B4D"

    Cursor.execute(
            "SELECT * FROM settings WHERE user_id = ?",
            (call.message.chat.id,)
        )
    result=Cursor.fetchone()
    
    if result:
        Cursor.execute("""
                        UPDATE settings
                        SET background_color = ?,
                            background_type = ?
                        WHERE user_id = ?
                        """, (
                        back_color,
                        "color",
                        call.message.chat.id

                    ))
        bot.send_message(call.message.chat.id,'حله ✔',reply_markup=markup)
    else:
        Cursor.execute("""
                        INSERT INTO settings
                        (user_id, background_color, background_type)
                        VALUES (?, ?, ?)
                        """, (
                        call.message.chat.id,
                        back_color,
                        "color"
                    ))
        bot.send_message(call.message.chat.id,'حله ✔',reply_markup=markup)
    db.MAIN_DB.commit()
  

# endregion


# region font

# منو فونت
def choose_font(call):
    markup=telebot.types.InlineKeyboardMarkup()
    B_Nazanin=telebot.types.InlineKeyboardButton('B Nazanin',callback_data='Bnazanin_font')
    Rounded=telebot.types.InlineKeyboardButton('IRAN Rounded',callback_data='IranRounded_font')
    Mahtab=telebot.types.InlineKeyboardButton('Digi Mahtab',callback_data='DigiMahtab_font')
    markup.add(B_Nazanin,Rounded,Mahtab,row_width=1)

    bot.send_message(call.message.chat.id,'فونت دلخواهت رو انتخاب کن ✒',reply_markup=markup)

# تنظیم فونت
def set_font(call):
    markup=telebot.types.InlineKeyboardMarkup()
    settings_menuBtn=telebot.types.InlineKeyboardButton('منو تنظیمات ⚙',callback_data='settings_menu')
    main_menuBtn=telebot.types.InlineKeyboardButton('منو اصلی 🏠',callback_data='main_menu')
    markup.add(settings_menuBtn,main_menuBtn,row_width=1)

    font=call.data
    main_font=None
    match font:
        case 'Bnazanin_font':
            main_font="fonts/B-NAZANIN.TTF"
        case 'IranRounded_font':
            main_font="fonts/IRAN Rounded.ttf"
        case 'DigiMahtab_font':
            main_font="fonts/Digi Mahtab Bold.ttf"
      
    Cursor.execute(
            "SELECT * FROM settings WHERE user_id = ?",
            (call.message.chat.id,)
        )
    result=Cursor.fetchone()
    
    if result:
        Cursor.execute("""
                        UPDATE settings
                        SET font = ?
                        WHERE user_id = ?
                        """, (
                        main_font,
                        call.message.chat.id

                    ))
        bot.send_message(call.message.chat.id,'حله ✔',reply_markup=markup)
    else:
        Cursor.execute("""
                        INSERT INTO settings
                        (user_id, font)
                        VALUES (?, ?)
                        """, (
                        call.message.chat.id,
                        main_font,
                    ))
        bot.send_message(call.message.chat.id,'حله ✔',reply_markup=markup)
    db.MAIN_DB.commit()

# endregion


# region backruond

# منو بکگراند
def choose_background(call):
    markup=telebot.types.InlineKeyboardMarkup()
    jungle_btn=telebot.types.InlineKeyboardButton('جنگل',callback_data='back_jungle')
    sea_btn=telebot.types.InlineKeyboardButton('دریا',callback_data='back_sea')
    vir_btn=telebot.types.InlineKeyboardButton('کویر',callback_data='back_vir')
    sky_btn=telebot.types.InlineKeyboardButton('آسمان ',callback_data='back_sky')
    flower_btn=telebot.types.InlineKeyboardButton('گل',callback_data='back_flower')

    markup.add(jungle_btn,sea_btn,vir_btn,sky_btn,flower_btn,row_width=2)
    bot.send_message(call.message.chat.id,'روحیاتت با کدوم سازگاره ؟❄',reply_markup=markup)

# بکگراند 
def set_background(call):
    markup=telebot.types.InlineKeyboardMarkup()
    settings_menuBtn=telebot.types.InlineKeyboardButton('منو تنظیمات ⚙',callback_data='settings_menu')
    main_menuBtn=telebot.types.InlineKeyboardButton('منو اصلی 🏠',callback_data='main_menu')
    markup.add(settings_menuBtn,main_menuBtn,row_width=1)

    back_img=call.data
    background=None
    match back_img:
        case 'back_jungle':
           background="backgrounds/jungle.png"
        case 'back_sea':
            background="backgrounds/sea.png"
        case 'back_vir':
            background="backgrounds/vir.png"
        case 'back_sky':
            background="backgrounds/sky.png"
        case 'back_flower':
            background="backgrounds/flower.png"

    Cursor.execute(
            "SELECT * FROM settings WHERE user_id = ?",
            (call.message.chat.id,)
            )
    result=Cursor.fetchone()
    
    if result:
        Cursor.execute("""
                UPDATE settings
                SET background_type = ?,
                    background_path = ?
                WHERE user_id = ?
                """, (
                "image",
                background,
                call.message.chat.id

            ))
    else:
        Cursor.execute("""
                INSERT INTO settings
                (user_id, background_type, background_path)
                VALUES (?, ?, ?)
                """, (
                call.message.chat.id,
                "image",
                background
                ))
    bot.send_message(call.message.chat.id,'حله ✔',reply_markup=markup)
    db.MAIN_DB.commit()

      
    
      

# endregion


# ---------------------------------------inside bot-----------------------------------------

# region post maker

# generate image
def generate_img(my_text,message,mode):

    Cursor.execute(""" SELECT * FROM settings WHERE user_id = ? """ , (message.chat.id,))
    result=Cursor.fetchone()
    if result!=None:
        font=result[2]
        background_type = result[3]
        background_color = result[1]
        background_path = result[4]
    font_color="white"
    colors_list=["#55552F", "#3A4656" , "#670001" , "#3D392E" , "#866B4D", "#111111"]

    if mode=="post":
            img_size=(1080, 1080)
            abaad=(540,540)
    elif mode=="video":
        img_size=(1080, 1920)
        abaad=(540,960)
    
    if background_type == "color":
        post_background = background_color
        image =Image.new(
                "RGB",
                img_size,
                post_background
            )
        

    elif background_type == "image":
        post_background = Image.open(background_path).convert("RGB")
        image = post_background.resize(img_size)
        font_color="black"
    else:
        post_background = random.choice(colors_list)
        image =Image.new(
                "RGB",
                img_size,
                post_background
            )
                      

    if font==None:
        main_font="fonts/IRAN Rounded.ttf"
    else:
        main_font=font
    
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(
        main_font,
        60
    )

    wrapped_text = wrap_text(my_text,font, 900,draw)
    
    final_lines = []

    for line in wrapped_text.split("\n"):
        reshaped = arabic_reshaper.reshape(line)
        bidi_line = get_display(reshaped)
        final_lines.append(bidi_line)

    final_text = "\n".join(final_lines)

    draw.multiline_text(
        abaad,
        final_text,
        font=font,
        fill=font_color,
        anchor="mm",
        align="center",
        spacing=15
    )

    image_bytes=BytesIO()
    image.save(image_bytes,format="JPEG",quality=85,optimize=True)
    image_bytes.seek(0)
    if mode=="post":        
        bot.send_photo(message.chat.id,image_bytes,timeout=60)
    else:
        return image_bytes


# wrap text
def wrap_text(text, font, max_width, draw):
    words = text.split()
    final_lines = []
    current_line = ""

    for word in words:
        if not current_line:
            test_line = word
        else:
            test_line = current_line + " " + word

        bbox = draw.textbbox(
            (0, 0),
            test_line,
            font=font,
           
        )

        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                final_lines.append(current_line)

            current_line = word

    if current_line:
        final_lines.append(current_line)

    return "\n".join(final_lines)



# endregion

# region video maker
def make_video(message,picture):
    image = ImageClip(picture)
    video = image.with_duration(10)
    audio = AudioFileClip("music/music_main.mp3")
    main_audio = audio.subclipped(0, 10)
    main_video = video.with_audio(main_audio)

    output_path = f"temp/reel_{message.chat.id}.mp4"

    main_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac"
    )
    print(
    "Video size:",
    os.path.getsize(output_path) / (1024 * 1024),
    "MB"
)
    video.close()
    audio.close()
    main_video.close()

    try:
        with open(output_path, "rb") as video_file:
            bot.send_video(message.chat.id,video_file,timeout=120)

    finally:

        if os.path.exists(output_path):
            os.remove(output_path)

# endregion



bot.infinity_polling()

