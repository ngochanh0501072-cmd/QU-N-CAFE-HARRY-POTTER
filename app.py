import streamlit as st
import pandas as pd
import sqlite3
import random
import time
import json
from datetime import datetime

# ==========================================
# 1. DATABASE SETUP & INITIALIZATION
# ==========================================
def init_db():
    conn = sqlite3.connect('hogwarts_cafe.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            order_type TEXT,
            items TEXT,
            total_amount REAL,
            discount_amount REAL,
            final_amount REAL,
            voucher_used TEXT,
            payment_method TEXT,
            status TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Page configuration
st.set_page_config(
    page_title="Hogwarts Café & Elixirs",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'cart' not in st.session_state:
    st.session_state.cart = []
if 'applied_voucher' not in st.session_state:
    st.session_state.applied_voucher = None
if 'tarot_drawn' not in st.session_state:
    st.session_state.tarot_drawn = False
if 'drawn_card' not in st.session_state:
    st.session_state.drawn_card = None

# ==========================================
# 2. CUSTOM CSS & MAGICAL ANIMATIONS
# ==========================================
MAGICAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Quicksand:wght@400;600&display=swap');

    /* Global Dark Mystic Theme */
    .stApp {
        background: linear-gradient(135deg, #0b0710 0%, #170d27 50%, #08111e 100%);
        color: #e2d7f5;
        font-family: 'Quicksand', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cinzel', serif !important;
        color: #f3d068 !important;
        text-shadow: 0 0 10px rgba(243, 208, 104, 0.4);
    }

    /* Floating Hedwig Owl Animation */
    @keyframes floatOwl {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(3deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    .hedwig-container {
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 9999;
        pointer-events: none;
        animation: floatOwl 4s ease-in-out infinite;
    }

    /* Flying Broom Animation */
    @keyframes flyBroom {
        0% { left: -100px; transform: scaleX(1); }
        50% { transform: translateY(-20px) scaleX(1); }
        100% { left: 105vw; transform: scaleX(1); }
    }

    .flying-broom {
        position: fixed;
        top: 12%;
        z-index: 9998;
        font-size: 2.2rem;
        pointer-events: none;
        animation: flyBroom 18s linear infinite;
        opacity: 0.85;
    }

    /* Sparkles / Magic Glow */
    .magic-card {
        background: rgba(26, 18, 43, 0.75);
        border: 1px solid #d4af37;
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 20px rgba(212, 175, 55, 0.15);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    
    .magic-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(212, 175, 55, 0.35);
        border-color: #ffd700;
    }

    /* Tarot Cards UI */
    .tarot-card {
        background: linear-gradient(145deg, #1f1135, #0f081d);
        border: 2px solid #e0a96d;
        border-radius: 12px;
        text-align: center;
        padding: 20px;
        cursor: pointer;
        box-shadow: 0 0 15px rgba(186, 133, 255, 0.2);
        transition: transform 0.4s ease, box-shadow 0.4s ease;
    }

    .tarot-card:hover {
        transform: scale(1.05) rotate(1deg);
        box-shadow: 0 0 25px rgba(243, 208, 104, 0.6);
    }

    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7b2cbf 0%, #3a0ca3 100%) !important;
        color: #f3d068 !important;
        border: 1px solid #d4af37 !important;
        border-radius: 10px !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 700 !important;
        text-shadow: 0 0 5px rgba(0,0,0,0.5);
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #9d4edd 0%, #4cc9f0 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(212, 175, 55, 0.6) !important;
        transform: scale(1.02);
    }

    /* Badge */
    .badge-voucher {
        background-color: #2b1055;
        border: 1px dashed #ffd700;
        color: #ffd700;
        padding: 8px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #100a1c 0%, #08040f 100%);
        border-right: 1px solid #321f47;
    }
</style>

<!-- Floating Hedwig & Broom Animation Elements -->
<div class="hedwig-container">
    <div style="font-size: 3rem; filter: drop-shadow(0 0 10px rgba(255,255,255,0.6));">🦉📜</div>
</div>
<div class="flying-broom">
    🧹✨
</div>
"""
st.markdown(MAGICAL_CSS, unsafe_allow_html=True)

# ==========================================
# 3. MENU DATA DEFINITION (Harry Potter Vibe)
# ==========================================
MENU_ITEMS = {
    "☕ Cà Phê Độc Dược & Đồ Uống Ma Thuật": [
        {
            "id": "drink_1",
            "name": "Trà Sữa Bia Bơ Butterbeer",
            "price": 45000,
            "desc": "Thức uống lừng danh Làng Hogsmeade - vị béo ngậy kem bơ, đậm vị trà bí truyền.",
            "img": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "drink_2",
            "name": "Espresso Hơi Thở Rồng (Dragon Breath)",
            "price": 39000,
            "desc": "Cà phê đậm đặc chiết xuất từ hạt cà phê rang cùng vảy Rồng Trắng Na Uy.",
            "img": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "drink_3",
            "name": "Trà Độc Dược Biến Hình (Polyjuice Elixir)",
            "price": 49000,
            "desc": "Trà trái cây ma thuật đổi màu kì ảo khi khuấy đều, thanh mát huyền bí.",
            "img": "https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "drink_4",
            "name": "Cà Phê Sữa Bùa Mê Amortentia",
            "price": 42000,
            "desc": "Sữa tươi ngọt ngào hòa quyện espresso quyến rũ như tình dược lừng danh.",
            "img": "https://images.unsplash.com/photo-1572442388796-11668a67e53d?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "drink_5",
            "name": "Trà Matcha Bọ Cạp Tối Thượng",
            "price": 48000,
            "desc": "Matcha Uji nguyên chất thơm lừng đậm đà năng lượng phép thuật Slytherin.",
            "img": "https://images.unsplash.com/photo-1536256263959-770b48d82b0a?auto=format&fit=crop&w=600&q=80"
        }
    ],
    "🧹 Bánh Tráng & Đồ Ăn Vặt Ma Thuật": [
        {
            "id": "snack_1",
            "name": "Cá Viên Bội Phấn Phép Thuật",
            "price": 30000,
            "desc": "Cá viên chiên giòn rụm lắc bột phô mai kim cương rực rỡ ma thuật.",
            "img": "https://images.unsplash.com/photo-1562967914-608f82629710?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "snack_2",
            "name": "Khoai Tây Chiên Hòn Đá Phù Thủy",
            "price": 35000,
            "desc": "Khoai tây cắt lát vồng vàng ngọc, xóc muối tỏi ớt ma thuật béo bơ.",
            "img": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "snack_3",
            "name": "Bánh Tráng Cuộn Huyết Rồng (Tráng Phép)",
            "price": 28000,
            "desc": "Bánh tráng phơi sương cuộn sốt bơ trứng, sốt me cay xé lưỡi bùa yêu.",
            "img": "https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "snack_4",
            "name": "Snack Nhện Tóc Giòn Rụm",
            "price": 25000,
            "desc": "Snack vị cay giòn tan lấy cảm hứng từ Rừng Cấm ma mị.",
            "img": "https://images.unsplash.com/photo-1599490659213-e2b9527bd087?auto=format&fit=crop&w=600&q=80"
        },
        {
            "id": "snack_5",
            "name": "Xúc Xích Đũa Phép Phượng Hoàng",
            "price": 32000,
            "desc": "Xúc xích Đức nướng nguyên thanh dai giòn rưới sốt mù tạt mật ong ma thuật.",
            "img": "https://images.unsplash.com/photo-1541745537411-b8046dc6d66c?auto=format&fit=crop&w=600&q=80"
        }
    ]
}

TAROT_CARDS = [
    {
        "name": "Bậc Thầy Độc Dược (Severus Snape)",
        "voucher": "POTION10",
        "desc": "Giảm ngay 10% trên Tổng hóa đơn ma thuật!",
        "type": "percent",
        "value": 10,
        "icon": "🧪"
    },
    {
        "name": "Bùa Thoát Nợ (Alohomora)",
        "voucher": "FREETOPPING",
        "desc": "Tặng FREE 1 Topping Ma Thuật bất kỳ!",
        "type": "free_topping",
        "value": 10000,
        "icon": "🗝️"
    },
    {
        "name": "Nước Mắt Phượng Hoàng (Fawkes)",
        "voucher": "PHOENIX15K",
        "desc": "Hồi sinh ví tiền - Giảm thẳng 15.000 VNĐ!",
        "type": "fixed",
        "value": 15000,
        "icon": "🔥"
    },
    {
        "name": "Chiếc Cốc Lửa (Goblet of Fire)",
        "voucher": "FIREDRINK",
        "desc": "Bùa chú thịnh vượng - Giảm 20% cho Đồ uống!",
        "type": "percent_drink",
        "value": 20,
        "icon": "🏆"
    },
    {
        "name": "Mắt Kính Harry Potter",
        "voucher": "LUCKYPOTTER",
        "desc": "May mắn nhân đôi - Giảm 10.000 VNĐ cho đơn từ 50k!",
        "type": "fixed",
        "value": 10000,
        "icon": "👓"
    },
    {
        "name": "Bánh Quy Bội Phấn Gryffindor",
        "voucher": "SNACKFREE",
        "desc": "Bùa chú ngọt ngào - Giảm 12.000 VNĐ cho Đồ ăn vặt!",
        "type": "fixed",
        "value": 12000,
        "icon": "🦁"
    }
]

# Helper for formatted currency
def fmt_vnd(amount):
    return f"{int(amount):,} VNĐ".replace(",", ".")

# ==========================================
# 4. NAVIGATION & SIDEBAR HEADER
# ==========================================
st.sidebar.markdown("### 🏰 HOGWARTS NAVIGATION")
page = st.sidebar.radio(
    "Chọn sảnh ma thuật:",
    ["📜 Menu Đặt Món", "🔮 Mini Game Tarot", "🛒 Giỏ Hàng & Thanh Toán", "⚡ Tra Cứu Đơn Hàng", "👑 Admin Dashboard"],
    index=0
)

st.sidebar.markdown("---")
# Quick Cart View in Sidebar
cart_count = sum([item['qty'] for item in st.session_state.cart])
st.sidebar.markdown(f"🛒 **Giỏ hàng hiện tại:** `{cart_count} món`")
if st.session_state.applied_voucher:
    st.sidebar.markdown(f"🎟️ **Voucher đã chọn:** `{st.session_state.applied_voucher['voucher']}`")

st.sidebar.markdown("---")
st.sidebar.info("✨ *Lời khuyên ma thuật:* Bốc bài Tarot trước khi chốt đơn để săn Voucher giảm giá hấp dẫn!")

# Header Banner
st.markdown("""
<div style="text-align: center; padding: 15px 0 25px 0;">
    <h1 style="font-size: 3rem; margin-bottom: 5px;">🏰 HOGWARTS CAFÉ & ELIXIRS 🔮</h1>
    <p style="font-style: italic; color: #d4af37; font-size: 1.1rem;">
        "Nơi thưởng thức Độc dược huyền bí & Đồ ăn vặt Ma thuật tại thế giới Phù thủy"
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. PAGE 1: MINI GAME TAROT
# ==========================================
if page == "🔮 Mini Game Tarot":
    st.subheader("🔮 Bói Bài Tarot Phù Thủy - Nhận Voucher Ma Thuật")
    st.write("Hãy dùng trực giác phép thuật của bạn để chọn 1 lá bài dưới đây. Mỗi lá bài mang một lời chúc và một đặc quyền ưu đãi dành riêng cho bạn!")

    if not st.session_state.tarot_drawn:
        cols = st.columns(3)
        for idx, card in enumerate(TAROT_CARDS):
            col = cols[idx % 3]
            with col:
                st.markdown(f"""
                <div class="tarot-card">
                    <div style="font-size: 3.5rem;">🔮</div>
                    <h4 style="margin-top: 10px;">Lá Bài #{idx + 1}</h4>
                    <p style="font-size: 0.85rem; color: #a992cb;">Ẩn chứa bùa chú bí mật</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"✨ Lật lá #{idx + 1}", key=f"tarot_btn_{idx}", use_container_width=True):
                    st.session_state.tarot_drawn = True
                    st.session_state.drawn_card = card
                    st.session_state.applied_voucher = card
                    st.rerun()
    else:
        card = st.session_state.drawn_card
        st.balloons()
        st.markdown(f"""
        <div class="magic-card" style="text-align: center; padding: 30px; border: 2px solid #ffd700;">
            <div style="font-size: 5rem;">{card['icon']}</div>
            <h2 style="color: #ffd700;">{card['name']}</h2>
            <div class="badge-voucher" style="font-size: 1.3rem;">VOUCHER: {card['voucher']}</div>
            <h3 style="color: #4cc9f0; margin-top: 15px;">{card['desc']}</h3>
            <p style="margin-top: 10px; color: #e2d7f5;">Voucher đã được tự động lưu vào Giỏ hàng của bạn!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Bốc lại bài (Làm mới may mắn)", use_container_width=True):
            st.session_state.tarot_drawn = False
            st.session_state.drawn_card = None
            st.rerun()

# ==========================================
# 6. PAGE 2: MENU & STEP-BY-STEP ORDERING
# ==========================================
elif page == "📜 Menu Đặt Món":
    st.subheader("📜 Thực Đơn Phép Thuật Hogwarts")

    if st.session_state.applied_voucher:
        v = st.session_state.applied_voucher
        st.success(f"🎟️ **Voucher Ma Thuật đang kích hoạt:** {v['name']} ({v['desc']})")

    # Category Tabs
    categories = list(MENU_ITEMS.keys())
    tab1, tab2 = st.tabs(categories)

    def render_category_menu(category_name):
        items = MENU_ITEMS[category_name]
        for item in items:
            with st.container():
                cols = st.columns([1, 2.5, 1.5])
                with cols[0]:
                    st.image(item['img'], use_column_width=True)
                with cols[1]:
                    st.markdown(f"### {item['name']}")
                    st.markdown(f"*{item['desc']}*")
                    st.markdown(f"**Giá gốc:** <span style='color:#ffd700; font-size:1.2rem; font-weight:bold;'>{fmt_vnd(item['price'])}</span>", unsafe_allow_html=True)
                
                with cols[2]:
                    # Step-by-step detail selector
                    with st.popover(f"➕ Chọn / Tùy chỉnh", use_container_width=True):
                        st.markdown(f"#### Tùy chỉnh: {item['name']}")
                        
                        # Size selection (Only for drinks)
                        is_drink = "☕" in category_name
                        size = "Mặc định"
                        size_price_add = 0
                        
                        if is_drink:
                            size = st.radio(
                                "1️⃣ Chọn Size:",
                                ["Size S (-5k)", "Size M (Chuẩn)", "Size L (+8k)"],
                                index=1,
                                key=f"size_{item['id']}"
                            )
                            if "Size S" in size:
                                size_price_add = -5000
                            elif "Size L" in size:
                                size_price_add = 8000
                        
                        # Sweetness & Ice (Only for drinks)
                        sweetness = "100% Đường"
                        ice = "100% Đá"
                        if is_drink:
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                sweetness = st.selectbox(
                                    "2️⃣ Mức Đường:",
                                    ["100% Đường", "70% Đường", "50% Đường", "30% Đường", "Không đường (0%)"],
                                    key=f"sweet_{item['id']}"
                                )
                            with col_s2:
                                ice = st.selectbox(
                                    "3️⃣ Mức Đá:",
                                    ["100% Đá", "70% Đá", "50% Đá", "Ít đá", "Không đá"],
                                    key=f"ice_{item['id']}"
                                )

                        # Topping Options
                        toppings = []
                        topping_total = 0
                        if is_drink:
                            st.markdown("4️⃣ **Topping Ma Thuật (+10.000đ/loại):**")
                            top1 = st.checkbox("Trân châu Đen Lời Nguyền (+10k)", key=f"top1_{item['id']}")
                            top2 = st.checkbox("Thạch Sương Mù Mắt Rồng (+10k)", key=f"top2_{item['id']}")
                            top3 = st.checkbox("Kem Bơ Bội Phấn (+10k)", key=f"top3_{item['id']}")
                            
                            if top1: 
                                toppings.append("Trân châu Đen")
                                topping_total += 10000
                            if top2: 
                                toppings.append("Thạch Sương Mù")
                                topping_total += 10000
                            if top3: 
                                toppings.append("Kem Bơ Bội Phấn")
                                topping_total += 10000
                        else:
                            st.markdown("1️⃣ **Sốt Extra (+5.000đ):**")
                            extra1 = st.checkbox("Sốt Bơ Trứng Bùa Yêu (+5k)", key=f"ext1_{item['id']}")
                            extra2 = st.checkbox("Bột Phô Mai Kim Cương (+5k)", key=f"ext2_{item['id']}")
                            if extra1:
                                toppings.append("Sốt Bơ Trứng")
                                topping_total += 5000
                            if extra2:
                                toppings.append("Bột Phô Mai")
                                topping_total += 5000

                        # Note for Barista/Kitchen
                        note = st.text_input("📝 Ghi chú cho Quán (VD: Giòn nhiều, ít cay...):", key=f"note_{item['id']}")
                        
                        qty = st.number_input("Số lượng:", min_value=1, max_value=20, value=1, key=f"qty_{item['id']}")
                        
                        final_item_price = item['price'] + size_price_add + topping_total

                        if st.button("🛒 Thêm vào Giỏ Hàng", key=f"add_btn_{item['id']}", use_container_width=True):
                            cart_entry = {
                                "id": item['id'],
                                "name": item['name'],
                                "base_price": item['price'],
                                "final_unit_price": final_item_price,
                                "size": size,
                                "sweetness": sweetness,
                                "ice": ice,
                                "toppings": toppings,
                                "note": note,
                                "qty": qty,
                                "category": category_name
                            }
                            st.session_state.cart.append(cart_entry)
                            st.toast(f"✅ Đã thêm {qty}x {item['name']} vào giỏ hàng!", icon="✨")
                            st.rerun()

                st.markdown("<hr style='border: 0.5px solid #321f47;'>", unsafe_allow_html=True)

    with tab1:
        render_category_menu(categories[0])
    with tab2:
        render_category_menu(categories[1])

# ==========================================
# 7. PAGE 3: CART & CHECKOUT
# ==========================================
elif page == "🛒 Giỏ Hàng & Thanh Toán":
    st.subheader("🛒 Giỏ Hàng Phép Thuật & Checkout")

    if not st.session_state.cart:
        st.info("🔮 Giỏ hàng của bạn đang trống! Hãy quay lại Thực Đơn để chọn món nhé.")
    else:
        col_c1, col_c2 = st.columns([1.8, 1.2])

        with col_c1:
            st.markdown("### 📋 Danh Sách Món Đã Chọn")
            subtotal = 0
            
            for idx, item in enumerate(st.session_state.cart):
                item_total = item['final_unit_price'] * item['qty']
                subtotal += item_total
                
                with st.expander(f"🔹 {item['qty']}x {item['name']} - {fmt_vnd(item_total)}", expanded=True):
                    st.write(f"- **Đơn giá:** {fmt_vnd(item['final_unit_price'])}")
                    if "☕" in item['category']:
                        st.write(f"- **Size:** {item['size']} | **Đường:** {item['sweetness']} | **Đá:** {item['ice']}")
                    if item['toppings']:
                        st.write(f"- **Toppings/Extra:** {', '.join(item['toppings'])}")
                    if item['note']:
                        st.write(f"- **Ghi chú riêng:** *{item['note']}*")
                    
                    if st.button("🗑️ Xóa món này", key=f"del_{idx}"):
                        st.session_state.cart.pop(idx)
                        st.rerun()

            if st.button("🧹 Xóa sạch giỏ hàng"):
                st.session_state.cart = []
                st.rerun()

        with col_c2:
            st.markdown("### 💳 Tổng Chi Phí & Voucher")
            
            # Voucher Calculation
            discount = 0
            voucher_info = st.session_state.applied_voucher
            
            if voucher_info:
                v_type = voucher_info['type']
                v_val = voucher_info['value']
                
                if v_type == "percent":
                    discount = subtotal * (v_val / 100)
                elif v_type == "fixed":
                    discount = v_val
                elif v_type == "free_topping":
                    discount = 10000
                elif v_type == "percent_drink":
                    drink_total = sum([i['final_unit_price'] * i['qty'] for i in st.session_state.cart if "☕" in i['category']])
                    discount = drink_total * (v_val / 100)

            discount = min(discount, subtotal)
            final_total = subtotal - discount

            st.write(f"**Tạm tính:** {fmt_vnd(subtotal)}")
            if voucher_info:
                st.write(f"**Voucher ({voucher_info['voucher']}):** -{fmt_vnd(discount)}")
            st.markdown(f"### **Tổng thanh toán:** <span style='color:#ffd700;'>{fmt_vnd(final_total)}</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 📝 Thông Tin Nhận Hàng")
            cust_name = st.text_input("Tên Phù Thủy / Khách hàng:", placeholder="VD: Harry Potter (Bàn 4)")
            order_type = st.radio("Hình thức nhận:", ["Tại Quán (Dùng tại bàn/Lấy ngay)", "Giao Tận Nơi (Ship Cú Hedwig)"])

            st.markdown("### 💰 Phương Thức Thanh Toán")
            pay_method = st.radio(
                "Chọn hình thức:",
                ["💵 Tiền mặt (Khi nhận hàng / Tại quầy)", "📱 Chuyển khoản VietQR / Ngân hàng"]
            )

            # VietQR Display
            if "Chuyển khoản" in pay_method:
                st.warning("⚡ Quét mã VietQR bên dưới để hoàn tất chuyển khoản:")
                
                # Mock Bank QR URL (VietQR standard format)
                bank_id = "MB"
                account_no = "0987654321"
                account_name = "HOGWARTS CAFE"
                memo = f"HOGWARTS_{int(time.time())}"
                
                qr_url = f"https://img.vietqr.io/image/{bank_id}-{account_no}-compact2.png?amount={int(final_total)}&addInfo={memo}&accountName={account_name}"
                
                st.image(qr_url, caption="Mã QR Thanh Toán Tự Động VietQR", use_column_width=True)
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 10px; border-radius: 8px; font-size: 0.9rem;'>
                    <b>Ngân hàng:</b> MB Bank<br>
                    <b>STK:</b> {account_no}<br>
                    <b>Chủ TK:</b> {account_name}<br>
                    <b>Nội dung CK:</b> <code>{memo}</code>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🔮 XÁC NHẬN ĐẶT HÀNG", use_container_width=True):
                if not cust_name:
                    st.error("⚠️ Vui lòng nhập Tên Phù Thủy / Khách hàng trước khi đặt!")
                else:
                    order_id = f"HW{random.randint(1000, 9999)}"
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Save to Database
                    conn = sqlite3.connect('hogwarts_cafe.db')
                    c = conn.cursor()
                    c.execute('''
                        INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        order_id,
                        cust_name,
                        order_type,
                        json.dumps(st.session_state.cart, ensure_ascii=False),
                        subtotal,
                        discount,
                        final_total,
                        voucher_info['voucher'] if voucher_info else "Không có",
                        pay_method,
                        "Đang pha chế 🧪",
                        created_at
                    ))
                    conn.commit()
                    conn.close()

                    st.balloons()
                    st.success(f"🎉 BÙA CHÚ THÀNH CÔNG! Đơn hàng #{order_id} đã được gửi đến nhà bếp Hogwarts!")
                    st.info("🦉 Cú Hedwig đang mang đơn hàng của bạn tới các Bậc thầy Độc dược!")
                    
                    # Reset Cart
                    st.session_state.cart = []
                    st.session_state.applied_voucher = None

# ==========================================
# 8. PAGE 4: TRACK ORDER
# ==========================================
elif page == "⚡ Tra Cứu Đơn Hàng":
    st.subheader("⚡ Tra Cứu Đơn Hàng Ma Thuật")
    search_id = st.text_input("Nhập Mã đơn hàng (VD: HW1234) hoặc Tên Phù Thủy:")

    conn = sqlite3.connect('hogwarts_cafe.db')
    df_orders = pd.read_sql_query("SELECT * FROM orders ORDER BY created_at DESC", conn)
    conn.close()

    if search_id:
        df_orders = df_orders[df_orders['order_id'].str.contains(search_id, case=False, na=False) | 
                              df_orders['customer_name'].str.contains(search_id, case=False, na=False)]

    if df_orders.empty:
        st.write("Không tìm thấy đơn hàng ma thuật nào phù hợp.")
    else:
        for _, row in df_orders.iterrows():
            with st.expander(f"⚡ Đơn #{row['order_id']} - {row['customer_name']} [{row['status']}]"):
                st.write(f"**Thời gian đặt:** {row['created_at']}")
                st.write(f"**Hình thức:** {row['order_type']} | **Thanh toán:** {row['payment_method']}")
                st.write(f"**Tổng tiền thanh toán:** {fmt_vnd(row['final_amount'])} (Voucher: {row['voucher_used']})")
                
                st.markdown("**Chi tiết món:**")
                items = json.loads(row['items'])
                for item in items:
                    st.write(f"- {item['qty']}x {item['name']} ({item['size']}) | Note: {item.get('note', 'Không')}")

# ==========================================
# 9. PAGE 5: ADMIN DASHBOARD
# ==========================================
elif page == "👑 Admin Dashboard":
    st.subheader("👑 Trang Quản Lý Bậc Thầy Hogwarts (Admin)")
    
    # Simple password protection
    admin_pass = st.text_input("Nhập Mật Mã Bộ Pháp Thuật:", type="password")
    if admin_pass != "hogwarts123":
        st.warning("🔒 Vui lòng nhập đúng mật mã Admin để xem Thống kê doanh thu (Mật khẩu mặc định: `hogwarts123`)")
    else:
        st.success("🔓 Xác minh danh tính thành công. Chào mừng Bậc thầy Quản lý!")

        conn = sqlite3.connect('hogwarts_cafe.db')
        df_orders = pd.read_sql_query("SELECT * FROM orders ORDER BY created_at DESC", conn)
        conn.close()

        if df_orders.empty:
            st.info("Chưa có dữ liệu đơn hàng nào.")
        else:
            # High level metrics
            total_rev = df_orders['final_amount'].sum()
            total_orders = len(df_orders)
            avg_order = df_orders['final_amount'].mean() if total_orders > 0 else 0

            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("💰 Tổng Doanh Thu", fmt_vnd(total_rev))
            col_m2.metric("📦 Tổng Số Đơn", f"{total_orders} đơn")
            col_m3.metric("📊 Giá Trị Trung Bình/Đơn", fmt_vnd(avg_order))

            st.markdown("---")
            st.markdown("### 📊 Thống Kê & Đơn Hàng Chi Tiết")

            # Status Update Functionality
            for idx, row in df_orders.iterrows():
                col_a1, col_a2 = st.columns([3, 1])
                with col_a1:
                    st.markdown(f"**Mã đơn #{row['order_id']}** | Khách: `{row['customer_name']}` | Tổng: `{fmt_vnd(row['final_amount'])}` | PTTT: `{row['payment_method']}`")
                    items_str = ", ".join([f"{i['qty']}x {i['name']}" for i in json.loads(row['items'])])
                    st.caption(f"Món: {items_str}")
                
                with col_a2:
                    new_status = st.selectbox(
                        "Trạng thái:",
                        ["Đang pha chế 🧪", "Đang giao 🧹", "Hoàn thành ✅", "Đã hủy ❌"],
                        index=["Đang pha chế 🧪", "Đang giao 🧹", "Hoàn thành ✅", "Đã hủy ❌"].index(row['status']) if row['status'] in ["Đang pha chế 🧪", "Đang giao 🧹", "Hoàn thành ✅", "Đã hủy ❌"] else 0,
                        key=f"status_select_{row['order_id']}"
                    )
                    
                    if new_status != row['status']:
                        conn = sqlite3.connect('hogwarts_cafe.db')
                        c = conn.cursor()
                        c.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, row['order_id']))
                        conn.commit()
                        conn.close()
                        st.toast(f"Đã cập nhật đơn #{row['order_id']} thành {new_status}")
                        st.rerun()

                st.markdown("<hr style='border: 0.2px solid #28153d;'>", unsafe_allow_html=True)

            # Export Raw Data
            st.markdown("### 📥 Export Dữ Liệu")
            st.download_button(
                label="📥 Tải Báo Cáo Doanh Thu (CSV)",
                data=df_orders.to_csv(index=False).encode('utf-8'),
                file_name=f"hogwarts_cafe_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
