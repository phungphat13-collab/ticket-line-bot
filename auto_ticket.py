def auto_login(self, username, password):
    """Tự động đăng nhập với username/password"""
    print("🔐 Đang thực hiện tự động đăng nhập...")
    
    try:
        self.driver.get("https://newticket.tgdd.vn/ticket")
        time.sleep(3)
        
        # Thử các selector cho username
        username_selectors = [
            "//input[@name='username']",
            "//input[@id='username']", 
            "//input[@type='text' and contains(@placeholder, 'user')]",
            "//input[@placeholder='Username']",
            "//input[@name='email']",
        ]
        
        # Thử các selector cho password
        password_selectors = [
            "//input[@type='password']",
            "//input[@name='password']",
            "//input[@id='password']",
        ]
        
        # Tìm và điền username
        username_field = None
        for selector in username_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        username_field = element
                        break
                if username_field:
                    break
            except:
                continue
        
        if not username_field:
            print("❌ Không tìm thấy trường username")
            return False
        
        username_field.clear()
        username_field.send_keys(username)
        print("✅ Đã điền username")
        
        # Tìm và điền password
        password_field = None
        for selector in password_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        password_field = element
                        break
                if password_field:
                    break
            except:
                continue
        
        if not password_field:
            print("❌ Không tìm thấy trường password")
            return False
        
        password_field.clear()
        password_field.send_keys(password)
        print("✅ Đã điền password")
        
        # Tìm và click nút đăng nhập
        login_selectors = [
            "//button[@type='submit']",
            "//input[@type='submit']",
            "//button[contains(text(), 'Đăng nhập')]",
            "//button[contains(text(), 'Login')]",
            "//button[contains(@class, 'btn-login')]",
        ]
        
        for selector in login_selectors:
            try:
                login_btn = self.driver.find_element(By.XPATH, selector)
                if login_btn.is_displayed() and login_btn.is_enabled():
                    print("🖱️ Đang click nút đăng nhập...")
                    login_btn.click()
                    time.sleep(5)
                    
                    # Kiểm tra đăng nhập thành công
                    if "login" not in self.driver.current_url.lower():
                        print("✅ Đăng nhập thành công!")
                        return True
                    else:
                        print("❌ Đăng nhập thất bại - vẫn ở trang login")
                        return False
            except Exception as e:
                continue
        
        print("❌ Không tìm thấy nút đăng nhập")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi đăng nhập tự động: {e}")
        return False