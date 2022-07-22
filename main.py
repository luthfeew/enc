# import library
import asyncio
from pyodide import create_proxy
from js import FileReader, Uint8Array, window, encodeURIComponent, File, Blob, URL

# deklarasi variable dari html
a_encrypt = Element("a_encrypt").element
a_decrypt = Element("a_decrypt").element
tab_encrypt = Element("tab_encrypt").element
tab_decrypt = Element("tab_decrypt").element
file_input = Element("file_input").element
file_name = Element("file_name").element
x_mode = Element("x_mode").element
x_key = Element("x_key").element
x_input = Element("x_input").element
x_output = Element("x_output").element
x_download = Element("x_download").element
x_download_name = Element("x_download_name").element
p_file = Element("p_file").element
p_key = Element("p_key").element
invalid_key = Element("invalid_key").element
cb_key = Element("cb_key").element
progress = Element("progress").element
progress2 = Element("progress2").element
chunk_total = Element("chunk_total").element
chunk_now = Element("chunk_now").element

# fungsi hapus input
def clear_input():
    x_input.value = ""
    x_output.value = ""
    file_name.innerHTML = "(kosong)"
    chunk_now.value = 0
    progress.value = 0
    progress2.value = 0


# fungsi hapus status file
def clear_state_file():
    p_file.innerHTML = ""
    file_name.style.borderColor = "#0a0a0a"


# fungsi hapus status kunci
def clear_state_key():
    p_key.innerHTML = ""
    x_key.classList.remove("is-danger")
    x_key.classList.add("is-black")
    invalid_key.classList.add("is-hidden")


# fungsi untuk menghandle perubahan input kunci
def key_input_change(event):
    clear_state_key()


# fungsi untuk menghandle checkbok tampilkan kunci
def checkbox_change(event):
    if cb_key.checked:
        x_key.type = "text"
    else:
        x_key.type = "password"


def progress_bar():
    chunk_now.value = int(chunk_now.value) + 1
    progress.value = int(chunk_now.value) / int(chunk_total.value) * 100


def progress_bar2():
    chunk_now.value = int(chunk_now.value) + 1
    progress2.value = int(chunk_now.value) / int(chunk_total.value) * 100


# fungsi untuk menghandle tab encrypt
def tab_encrypt_click(event):
    if not tab_encrypt.classList.contains("is-active"):
        x_mode.value = 1
        clear_state_file()
        clear_state_key()
        a_encrypt.style.borderColor = "#0a0a0a"
        a_decrypt.style.removeProperty("border-color")
        tab_encrypt.classList.add("is-active")
        tab_decrypt.classList.remove("is-active")
        x_download_name.innerHTML = "Enkripsi & Download"
        clear_input()


# fungsi untuk menghandle tab decrypt
def tab_decrypt_click(event):
    if not tab_decrypt.classList.contains("is-active"):
        x_mode.value = 0
        clear_state_file()
        clear_state_key()
        a_decrypt.style.borderColor = "#0a0a0a"
        a_encrypt.style.removeProperty("border-color")
        tab_decrypt.classList.add("is-active")
        tab_encrypt.classList.remove("is-active")
        x_download_name.innerHTML = "Dekripsi & Download"
        clear_input()


# fungsi untuk menghandle perubahan input file
async def file_input_change(event):
    progress.value = 0
    clear_state_file()
    # baca file yang diupload
    fileList = file_input.files
    for f in fileList:
        size = f.size
        chunk_size = 500000
        chunk_count = int(size / chunk_size) + 1
        chunk_total.value = chunk_count
        if size > chunk_size or size > 0:
            # jika mode enkripsi
            if int(x_mode.value) == 1:
                x_input.value = "abcdefghijklmnopqrstuvwxyz|||||"
                n = 0
                while n < chunk_count:
                    reader = FileReader.new()
                    reader.addEventListener("load", create_proxy(write_buffer_hex))
                    reader.readAsArrayBuffer(
                        f.slice(n * chunk_size, (n + 1) * chunk_size)
                    )
                    await asyncio.sleep(0.1)
                    n += 1
                    progress_bar()
            # jika mode dekripsi
            else:
                n = 0
                while n < chunk_count:
                    reader = FileReader.new()
                    reader.addEventListener("load", create_proxy(write_buffer_text))
                    reader.readAsText(f.slice(n * chunk_size, (n + 1) * chunk_size))
                    await asyncio.sleep(0.1)
                    n += 1
                    progress_bar()
        file_name.innerHTML = f.name

    file_input.value = ""


# fungsi untuk convert array buffer ke hex
def write_buffer_hex(event):
    x = Uint8Array.new(event.target.result)

    hex = ""
    for i in range(len(x)):
        hex += "%02x" % x[i]

    x_input.value += hex


# fungsi untuk convert array buffer ke text
def write_buffer_text(event):
    x_input.value += event.target.result


# fungsi untuk mengenkripsi
def encrypt(raw_data, raw_key):
    key = raw_key.lower()

    num_key = []
    for i in range(len(key)):
        key1 = key[i]
        num_key.append(ord(key1) - 97)

    count = 0
    ciphertext = ""

    for i in range(len(raw_data)):
        char0 = raw_data[i]
        char = char0.lower()
        if char == " ":
            ciphertext += " "
        elif char == ".":
            ciphertext += "."
        elif char == "|":
            ciphertext += "|"
        elif char.isdigit():
            ciphertext += char
        elif char.isalpha():
            if count < len(num_key):
                key1 = num_key[count]
                ciphertext += chr((ord(char) + key1 - 97) % 26 + 97)
                count += 1
            if count == len(num_key):
                count = 0

    progress_bar2()
    x_output.value += ciphertext


# fungsi untuk mendekripsi
def decrypt(raw_data, raw_key):
    key = raw_key.lower()

    num_key = []
    for i in range(len(key)):
        key1 = key[i]
        num_key.append(ord(key1) - 97)

    count = 0
    plaintext = ""

    for i in range(len(raw_data)):
        char0 = raw_data[i]
        char = char0.lower()
        if char == " ":
            plaintext += " "
        elif char == ".":
            plaintext += "."
        elif char == "|":
            plaintext += "|"
        elif char.isdigit():
            plaintext += char
        elif char.isalpha():
            if count < len(num_key):
                key1 = num_key[count]
                plaintext += chr((ord(char) - key1 - 97) % 26 + 97)
                count += 1
            if count == len(num_key):
                count = 0

    progress_bar2()
    x_output.value += plaintext


# fungsi untuk menghandle tombol download
async def download_click(event):
    x_output.value = ""
    x_download.classList.add("is-loading")
    key = x_key.value

    # validasi file yang diupload dan kunci
    if file_name.innerHTML == "(kosong)" or not key or len(key) < 2 or len(key) > 25:
        if file_name.innerHTML == "(kosong)":
            file_name.style.borderColor = "#f14668"
            p_file.classList.add("help", "is-danger")
            p_file.innerHTML = "Pilih file terlebih dahulu."
        if not key or len(key) < 2 or len(key) > 25:
            x_key.classList.remove("is-black")
            x_key.classList.add("is-danger")
            p_key.classList.add("help", "is-danger")
            p_key.innerHTML = "Kunci harus terdiri dari 2-25 karakter."
        return

    # split data menjadi chunk
    size = len(x_input.value)
    chunk_size = 1024 * 500
    chunk_count = int(size / chunk_size) + 1
    chunk_total.value = chunk_count
    chunk_now.value = 0

    # jika mode enkripsi
    if int(x_mode.value) == 1:
        for i in range(chunk_count):
            raw_data = x_input.value[i * chunk_size : (i + 1) * chunk_size]
            encrypt(raw_data, key)
            await asyncio.sleep(0.01)

        # buat element untuk download file yang telah dienkripsi
        link = window.document.createElement("a")
        link.setAttribute(
            "href",
            "data:text/plain;charset=utf-8," + encodeURIComponent(x_output.value),
        )
        link.setAttribute("download", file_name.innerHTML + ".enc")
        link.click()
    # jika mode dekripsi
    else:
        for i in range(chunk_count):
            raw_data = x_input.value[i * chunk_size : (i + 1) * chunk_size]
            decrypt(raw_data, key)
            await asyncio.sleep(0.01)

        key_valid = x_output.value.find("abcdefghijklmnopqrstuvwxyz", 0, 30)

        # validasi kunci
        # jika kunci tidak valid
        if key_valid == -1:
            invalid_key.classList.remove("is-hidden")
            return
        # jika kunci valid
        else:
            x = x_output.value.split("|||||")

        # proses mengembalikan file yang telah dienkripsi ke bentuk file yang asli
        uint8 = []
        for i in range(0, len(x[1]), 2):
            uint8.append(int(x[1][i : i + 2], 16))
        raw_uint8 = Uint8Array.new(uint8)
        raw_arraybuffer = raw_uint8.buffer
        file = File.new(
            [raw_arraybuffer],
            str(file_name.innerHTML[0:-4]),
            {"type": "application/octet-stream"},
        )
        file_blob = Blob.new([file], {"type": "application/octet-stream"})
        file_url = URL.createObjectURL(file_blob)

        # buat element untuk download file yang telah didekripsi
        link = window.document.createElement("a")
        link.setAttribute(
            "href",
            file_url,
        )
        link.setAttribute("download", str(file_name.innerHTML[0:-4]))
        link.click()

    x_download.classList.remove("is-loading")


# fungsi main
def main():
    # definisikan event listener/handler
    tab_encrypt.addEventListener("click", create_proxy(tab_encrypt_click))
    tab_decrypt.addEventListener("click", create_proxy(tab_decrypt_click))
    file_input.addEventListener("change", create_proxy(file_input_change))
    x_key.addEventListener("input", create_proxy(key_input_change))
    x_download.addEventListener("click", create_proxy(download_click))
    cb_key.addEventListener("change", create_proxy(checkbox_change))


# menjalankan fungsi main
main()
