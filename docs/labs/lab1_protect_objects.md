
# Protect a VM:
1. List VMs to be protected: 
    ```
    $ rbkcli vmware vm -s id,name,effectiveSlaDomainName -T
     id                                                           | name        | effectiveSlaDomainName
    =====================================================================================================
     VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-149 | windows2016 | Unprotected
     VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-148 | ubuntu1404  | Unprotected
     VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-147 | ubuntu-lamp | Unprotected
    
    **Total amount of objects [3]
    
    ```
    - In this case I want to protect the VM `windows2016`, so will use the ID `VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-149`

2. Search for command that assigns SLAs
    ```
    $ rbkcli commands -f endpoint~assign -T
    ```

3. Get and read documentation for that found API:
    ```
    $ rbkcli sla_domain id assign -m post -d
    ```

4. Protect the VM:
    ```
    $ rbkcli sla_domain 4c399fc1-f7f0-48f0-8eda-bbf1c8640582 assign -m post -p '{"managedIds": ["VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-149"]}'
    Response code: 204
    Response text:
    ```

5. Verify SLA assignment on VMs.
    ```
    $ rbkcli vmware vm -s id,name,effectiveSlaDomainName -T
     id                                                           | name        | effectiveSlaDomainName
    =====================================================================================================
     VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-149 | windows2016 | 2Hours
     VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-148 | ubuntu1404  | Unprotected
     VirtualMachine:::72ef7f2b-9149-4259-898b-e7edcccd0442-vm-147 | ubuntu-lamp | Unprotected
    
    **Total amount of objects [3]
    
    ```


<-- Back to [Useful learning workflows](labs.md)
