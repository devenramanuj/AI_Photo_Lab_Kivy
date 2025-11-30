import streamlit as st
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import io

# AI Library (rembg)
# Streamlit Cloud પર rembg[cpu] ઇન્સ્ટોલ કરવું જરૂરી છે.
try:
    # rembg[cpu] માટેની જરૂરિયાતો પૂરી કરવી
    from rembg import remove
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    
# --- મુખ્ય વેબ એપ ફંક્શન ---
def main():
    # Streamlit ની પેજ કોન્ફિગરેશન
    st.set_page_config(
        page_title="AI Photo Lab - Web Editor",
        layout="wide"
    )
    
    # 📌 PC સ્ક્રીન માટે મહત્તમ પહોળાઈ સેટ કરવા માટે CSS ઉમેરો
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
            max-width: 1200px; /* મહત્તમ પહોળાઈ સેટ */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Session State Initialization
    if 'image_state' not in st.session_state:
        st.session_state['image_state'] = None
    if 'filter_stack' not in st.session_session:
        st.session_state['filter_stack'] = []
    
    # હેડર
    st.title("📸 AI PHOTO LAB (Web Version)")
    st.markdown("---")
    
    # ફાઈલ અપલોડર
    uploaded_file = st.file_uploader("🖼️ ફોટો અપલોડ કરો", type=["jpg", "jpeg", "png"])

    # જો કોઈ નવી ફાઇલ અપલોડ થાય, તો સ્ટેટ અપડેટ કરો
    if uploaded_file is not None:
        try:
            new_image = Image.open(uploaded_file).convert("RGB")
            if st.session_state['image_state'] is None or uploaded_file.name != st.session_state.get('file_name', ''):
                st.session_state['image_state'] = new_image
                st.session_state['filter_stack'] = []
                st.session_state['file_name'] = uploaded_file.name
                st.success(f"ફાઇલ અપલોડ થઈ: {uploaded_file.name}")
        except Exception as e:
            st.error(f"ફોટો લોડ કરવામાં ભૂલ: {e}")
            st.session_state['image_state'] = None
    
    # જો કોઈ ઇમેજ લોડ થયેલી હોય તો જ કંટ્રોલ્સ દર્શાવો
    if st.session_state['image_state'] is not None:
        
        original_image = st.session_state['image_state'].copy()
        processed_image = original_image.copy() # Pipeline ની શરૂઆત

        # --- ડાબી બાજુ: કંટ્રોલ પેનલ (સાઇડબારમાં) ---
        st.sidebar.header("⚙️ એડિટિંગ કંટ્રોલ")
        
        # --- ૧. કલર એડજસ્ટમેન્ટ (સ્લાઇડર્સ) ---
        st.sidebar.markdown("### કલર અને લાઇટ એડજસ્ટમેન્ટ")
        brightness_val = st.sidebar.slider("બ્રાઇટનેસ", 0.1, 2.0, 1.0, 0.1, key="brightness")
        contrast_val = st.sidebar.slider("કોન્ટ્રાસ્ટ", 0.1, 2.0, 1.0, 0.1, key="contrast")
        saturation_val = st.sidebar.slider("સંતૃપ્તિ (Saturation)", 0.0, 2.0, 1.0, 0.1, key="saturation")
        sharpness_val = st.sidebar.slider("તીક્ષ્ણતા (Sharpness)", 0.0, 2.0, 1.0, 0.1, key="sharpness")
        
        # --- ૨. ટ્રાન્સફોર્મેશન (રોટેટ/ફ્લિપ) ---
        st.sidebar.markdown("### ટ્રાન્સફોર્મેશન")
        col_t1, col_t2, col_t3 = st.sidebar.columns(3)
        
        if col_t1.button("↩️ 90° રોટેટ"):
            st.session_state['image_state'] = st.session_state['image_state'].rotate(-90, expand=True)
            st.rerun() 
        
        if col_t2.button("↔️ હોરિઝોન્ટલ ફ્લિપ"):
            st.session_state['image_state'] = st.session_state['image_state'].transpose(Image.FLIP_LEFT_RIGHT)
            st.rerun() 
            
        custom_rotate = st.sidebar.slider("કસ્ટમ રોટેટ (Angle)", -180, 180, 0, key="custom_rotate")
        
        # --- ૩. Blur/Sharpen/Special Filters ---
        st.sidebar.markdown("### ઇફેક્ટ્સ અને ફિલ્ટર્સ")
        
        blur_val = st.sidebar.slider("બ્લર લેવલ", 0, 5, 0, 1, key="blur_level")
        sharpen_effect = st.sidebar.button("✨ EDGE ENHANCE", key="edge_enhance")
        
        col_s1, col_s2 = st.sidebar.columns(2)
        if col_s1.button("🪧 Posterize"):
            st.session_state['filter_stack'].append('posterize')
            st.rerun()
        if col_s2.button("☀️ Solarize"):
            st.session_state['filter_stack'].append('solarize')
            st.rerun()
        
        # AI અને બેઝિક ફિલ્ટર્સ
        col_f1, col_f2, col_f3 = st.sidebar.columns(3)
        
        if col_f1.button("⚫ B&W"):
            st.session_state['filter_stack'].append('bw')
            st.rerun()
        
        if col_f2.button("🟤 Sepia"):
            st.session_state['filter_stack'].append('sepia')
            st.rerun()
            
        if col_f3.button("🤖 AI Remove BG"):
            if AI_AVAILABLE:
                st.session_state['filter_stack'].append('rembg')
                st.rerun()
            else:
                st.error("rembg લાઈબ્રેરી ઇન્સ્ટોલ નથી.")
                
        # --- ૫. રીસેટ બટન ---
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 બધા ફેરફારો રીસેટ કરો"):
            uploaded_file.seek(0)
            st.session_state['image_state'] = Image.open(uploaded_file).convert("RGB") 
            st.session_state['filter_stack'] = [] 
            st.success("રીસેટ સફળ!")
            st.rerun()
        
        # --- એડિટિંગ લોજિક લાગુ કરો (Pipeline) ---
        
        # 1. કસ્ટમ રોટેટ લાગુ કરો
        if custom_rotate != 0:
            processed_image = processed_image.rotate(-custom_rotate, expand=True)

        # 2. ફિલ્ટર સ્ટેક લાગુ કરો
        for filter_name in st.session_state['filter_stack']:
            if filter_name == 'bw':
                processed_image = processed_image.convert("L").convert("RGB")
            elif filter_name == 'sepia':
                gray = processed_image.convert("L")
                processed_image = ImageOps.colorize(gray, "#3e2723", "#fff3e0").convert("RGB")
            elif filter_name == 'posterize':
                processed_image = ImageOps.posterize(processed_image, 4)
            elif filter_name == 'solarize':
                processed_image = ImageOps.solarize(processed_image, threshold=128)
            elif filter_name == 'rembg' and AI_AVAILABLE:
                try:
                    processed_image = remove(processed_image)
                    st.toast("✅ બેકગ્રાઉન્ડ રિમૂવ થયું!")
                except Exception as e:
                    st.error(f"AI ભૂલ: {e}")
        
        # 3. Blur/Sharpen/Edge Enhance લાગુ કરો
        if blur_val > 0:
            for _ in range(blur_val):
                processed_image = processed_image.filter(ImageFilter.BLUR)
        
        if sharpen_effect:
             processed_image = processed_image.filter(ImageFilter.EDGE_ENHANCE_MORE)

        # 4. સ્લાઇડર લોજિક લાગુ કરો (ImageEnhance)
        final_image = ImageEnhance.Brightness(processed_image).enhance(brightness_val)
        final_image = ImageEnhance.Contrast(final_image).enhance(contrast_val)
        final_image = ImageEnhance.Color(final_image).enhance(saturation_val)
        final_image = ImageEnhance.Sharpness(final_image).enhance(sharpness_val)

        # --- જમણી બાજુ: ડિસ્પ્લે અને ડાઉનલોડ ---
        st.header("✨ એડિટ કરેલો ફોટો")
        st.image(final_image, caption='તમારી વેબ એપમાં ફોટો', use_column_width=True)
        
        # ડાઉનલોડ બટન
        buf = io.BytesIO()
        final_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="💾 ફોટો ડાઉનલોડ કરો (PNG)",
            data=byte_im,
            file_name="edited_photo.png",
            mime="image/png"
        )
    else:
        st.info("કૃપા કરીને ફોટો એડિટિંગ શરૂ કરવા માટે એક ફાઇલ અપલોડ કરો.")

    # 📌 NEW FIX: સરળ Markdown Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>Devloped by - Devendra Ramanuj, 9276505035</p>", 
                unsafe_allow_html=True)


if __name__ == "__main__":
    main()
