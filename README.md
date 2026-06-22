# Bob Lab Assets

This repository was created to make it easier for lab participants to download the **txc-lab** files


## Access Bob

To access Bob, participants can either install the free 30-day trial version or use a VM provided by the instructor.

Option 1: Local Installation (Best Experience) 

Download: https://bob.ibm.com 

Action: Install the software and launch it to ensure it starts without permission errors. 

Note: This requires administrative rights on participants laptop. Their corporate IT group might need to approve the installation/configuration 

Option 2: Techzone VM

Instructor to reserve this environment https://techzone.ibm.com/collection/bob-enterprise-sales-assets and select `OCP-V RHEL 9 VM - Bob IDE (IBM-Bob-linux-x64-1.116.0+bob1.0.3)`

<img width="472" height="476" alt="image" src="https://github.com/user-attachments/assets/c632629c-6fe5-42d0-a5ea-72e6114f3320" />

Once the environment is provisioned, you can find the environment under the [Techzone Requests](https://techzone.ibm.com/my/requests?StatusFilter=%5B%22Ready%22%2C%22Scheduled%22%2C%22Provisioning%22%2C%22Pending+Approval%22%5D)

Open the `Environment` tab and you should see a link for the Console,user id and password.

<img width="1516" height="644" alt="image" src="https://github.com/user-attachments/assets/3b937c02-8e21-4486-86bb-cf97aac57bef" />

Confirmation: If you see a Linux desktop after signing in, you are all set. 

## Download the assets and install prerequisites
Open a terminal window (either on your local machine or on the VM provided by the instructor) and clone this repository:
```
git clone https://github.com/annumberhocker/bob-lab-assets
```

Change directory to the cloned repository and run the prerequisite script:
```
cd bob-lab-assets
./txc-lab-prereq.sh
```

This will unzip the assets and install the prerequisites (brew, python@3.12, uv, node, bc, openjdk maven)

## Lab Instructions

- Open and log in to IBM Bob

  - If using the VM, you should see a bar at the bottom with a dot grid
  
    <img width="485" height="94" alt="image" src="https://github.com/user-attachments/assets/4ad40b43-ddbc-451f-9e10-df824d1aa16e" />
    
  - Open the dot grid and select Bob

  - If locally installed, open the application panel and select Bob

    <img width="1400" height="574" alt="image" src="https://github.com/user-attachments/assets/c64383fe-b624-42df-bfb1-6fc1a49b7555" />

- Once Bob is opened, you should see a VSCode instance open with a panel like this:
  
  <img width="126" height="257" alt="image" src="https://github.com/user-attachments/assets/429ea25a-93c3-4301-bac3-b2a1e54bb7e9" />
 
- Click to “Open” a folder based on which lab you are wanting to complete:

  <img width="142" height="165" alt="image" src="https://github.com/user-attachments/assets/eb010a1f-5f2a-4745-9e59-b23dbf7c5a9f" />

  **Lab 1**: “Your Agentic AI Coding Partner”
  
  - open “txc-lab/agentic-lab” folder 
  - Choose “Yes I trust the Authors”.   
  - Instructions should pop up in a “Welcome” tab. If you are not seeing the tab, zoom out to make the font smaller
  
  **Lab 2a**: “Data Science with Bob”
  
  - open “txc-lab/datascience-lab” folder 
  - Choose “Yes I trust the Authors”.
  - Open the file “lab/step-by-step-lab.md” (right click on it and choose “Open in Preview”)
  
  **Lab 2b**: “Java Upgrade”
  
  - open “txc-lab/java-upgrade” folder 
  - Choose “Yes I trust the Authors”.   
  - Instructions should pop up in a “Welcome” tab 
