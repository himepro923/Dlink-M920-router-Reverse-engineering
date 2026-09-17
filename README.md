# Dlink-M920-router-Reverse-engineering
This repo is for all the info i can get from this router and maybe try to reuse it for something useful

so i have this old Dlink M920 router which i found so i thought i chould this to be useful i found it had normal Uart so i solder some pin headers
i bought a CH340G module
<img width="2304" height="4096" alt="PXL_20260913_140418894" src="https://github.com/user-attachments/assets/91fd3f40-ac37-4096-a20d-69d478a4db2a" />

<img width="1080" height="2400" alt="Screenshot_20260916_225745_com_hihonor_photos_SlotAlbumActivity" src="https://github.com/user-attachments/assets/c8a1b707-a385-4730-86f9-2a8e468e0a3b" />


and i got the output to work and from the logs i found this info:
CPU: Realtek rtl8197f-vg MIPS
RAM: 128MB DDR2 533Mhz
SPI: 16MB EON vendor Squashfs 4.0
Linux kernel: 3.10.90

and i also found out to enter the bootloader i have to spam ESC at the very start of the boot it not that useful but here all the commends
<img width="769" height="690" alt="PXL_20260914_145411815" src="https://github.com/user-attachments/assets/5cda7635-baa4-45db-b4aa-f99955704898" />


There are commends but i dont see them useful to me

and on to the rest of the boot the router littly dosnt ask for a user or password i just press enter and i got a root shell
<img width="454" height="116" alt="image" src="https://github.com/user-attachments/assets/d0906e7f-5dff-4f18-ad4c-129a620bb3b4" />

so i want to find the some useful commends first them i found out that the /tmp folder is RW and alot of free space 
<img width="660" height="278" alt="image" src="https://github.com/user-attachments/assets/4347a0b2-ac46-4929-adae-470dcb0d45a4" />

so i went my way to try to send file so i can run them i found the router had wget installed but it not useful to me since i dont have a laptop with a internet port

next i found why not send over uart so i made a script that uses printf to send the bytes to a file so it can build a 700k file took around 12mins
and i compiled the source code for 32bit MIPS of course with static option in gcc

i got some games to work like snake and doom cli that i send over my script you can find it in the repo
