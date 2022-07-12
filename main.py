import base64
from pyodide import create_proxy
from js import FileReader, Uint8Array, window, encodeURIComponent, File, Blob, URL

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


def clear_input():
    x_input.value = ""
    x_output.value = ""
    file_name.innerHTML = "(empty)"


def tab_encrypt_click(event):
    if not tab_encrypt.classList.contains("is-active"):
        x_mode.value = 1
        a_encrypt.style.borderColor = "#0a0a0a"
        a_decrypt.style.removeProperty("border-color")
        tab_encrypt.classList.add("is-active")
        tab_decrypt.classList.remove("is-active")
        x_download_name.innerHTML = "Encrypt & Download"
        clear_input()


def tab_decrypt_click(event):
    if not tab_decrypt.classList.contains("is-active"):
        x_mode.value = 0
        a_decrypt.style.borderColor = "#0a0a0a"
        a_encrypt.style.removeProperty("border-color")
        tab_decrypt.classList.add("is-active")
        tab_encrypt.classList.remove("is-active")
        x_download_name.innerHTML = "Decrypt & Download"
        clear_input()


async def file_input_change(event):
    fileList = file_input.files
    for f in fileList:
        reader = FileReader.new()
        if int(x_mode.value) == 1:
            x_input.value = f.name + "|||||"
            reader.readAsArrayBuffer(f)
            reader.onloadend = write_buffer_hex
        else:
            reader.readAsText(f)
            reader.onloadend = write_buffer_text
        file_name.innerHTML = f.name

    file_input.value = ""


def write_buffer_hex(event):
    x = Uint8Array.new(event.target.result)

    hex = ""
    for i in range(len(x)):
        hex += "%02x" % x[i]

    x_input.value += hex


def write_buffer_text(event):
    x_input.value = event.target.result


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
        if count < len(num_key):
            key1 = num_key[count]
            ciphertext += bytes([(ord(char0) + key1) % 256]).decode("latin-1")
            count += 1
        if count == len(num_key):
            count = 0

    return base64.a85encode(ciphertext.encode("utf-8")).decode("utf-8")


def decrypt(raw_data, raw_key):
    key = raw_key.lower()

    num_key = []
    for i in range(len(key)):
        key1 = key[i]
        num_key.append(ord(key1) - 97)

    ciphertext = base64.a85decode(raw_data).decode("utf-8")

    count = 0
    plaintext = ""

    for i in range(len(ciphertext)):
        char0 = ciphertext[i]
        if count < len(num_key):
            key1 = num_key[count]
            plaintext += bytes([(ord(char0) - key1) % 256]).decode("latin-1")
            count += 1
        if count == len(num_key):
            count = 0

    return plaintext


def download_click(event):
    if int(x_mode.value) == 1:
        x_output.value = encrypt(x_input.value, x_key.value)

        link = window.document.createElement("a")
        link.setAttribute(
            "href",
            "data:text/plain;charset=utf-8," + encodeURIComponent(x_output.value),
        )
        link.setAttribute("download", file_name.innerHTML + ".enc")
        link.click()
    else:
        x_output.value = decrypt(x_input.value, x_key.value)
        x = x_output.value.split("|||||")

        uint8 = []
        for i in range(0, len(x[1]), 2):
            uint8.append(int(x[1][i : i + 2], 16))
        raw_uint8 = Uint8Array.new(uint8)
        raw_arraybuffer = raw_uint8.buffer
        file = File.new([raw_arraybuffer], x[0], {"type": "application/octet-stream"})
        file_blob = Blob.new([file], {"type": "application/octet-stream"})
        file_url = URL.createObjectURL(file_blob)

        link = window.document.createElement("a")
        link.setAttribute(
            "href",
            file_url,
        )
        link.setAttribute("download", x[0])
        link.click()


def main():
    tab_encrypt.addEventListener("click", create_proxy(tab_encrypt_click))
    tab_decrypt.addEventListener("click", create_proxy(tab_decrypt_click))
    file_input.addEventListener("change", create_proxy(file_input_change))
    x_download.addEventListener("click", create_proxy(download_click))


main()