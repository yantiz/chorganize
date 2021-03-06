//
//  FirstViewController.swift
//  ChOrganizeApp
//
//  Created by Hana on 11/4/17.
//  Copyright © 2017 Pusheen Code. All rights reserved.
//

import UIKit

class ToDoViewController: UITableViewController {
    
    let sections = ["to-do", "completed"]
    var chores =  [[Chore]]()
    var choreNameToPass = ""
    var choreDateToPass = ""
    
    override func viewDidLoad() {
        super.viewDidLoad()
//        if chores.isEmpty {
//            loadToDoList()
//        }
        
        fetchChores()
        // This is supposed to help with reloading when a chore is created but...
        NotificationCenter.default.addObserver(self, selector: #selector(loadList), name: NSNotification.Name(rawValue: "loadToDoList"), object: nil)
    }
    
    func loadList(){
        chores = [[Chore]]()
        fetchChores()
        //load data here
        self.tableView.reloadData()
    }
    
    func fetchChores(){
        // Get Email
        self.chores.append([Chore]())
        self.chores.append([Chore]())
        
        let defaults = UserDefaults.standard
        let email: String = defaults.string(forKey: "email")!
        
        // Get Chores
        if let data = UserDefaults.standard.object(forKey: "groups") as? NSData {
            let groups = NSKeyedUnarchiver.unarchiveObject(with: data as Data) as! [Group]
            
            for group in groups {
                // Get completed chores
                getChores(email: email, groupID: group.id, completed: "false") {
                    (choreslist: [Chore]) in
                    if !choreslist.isEmpty {
                        for chore in choreslist {
                            self.chores[1].append(chore)
                        }
                    }
                    OperationQueue.main.addOperation {
                        self.tableView.reloadData()
                    }
                }
                
                // Get active chores
                getChores(email: email, groupID: group.id, completed: "true") {
                    (choreslist: [Chore]) in
                    if !choreslist.isEmpty {
                        for chore in choreslist {
                            self.chores[0].append(chore)
                        }
                    }
                    OperationQueue.main.addOperation {
                        self.tableView.reloadData()
                    }
                }
            }
        }
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    // Setup tableView
    override func numberOfSections(in tableView: UITableView) -> Int {
        return 2
    }
    
    override func tableView(_ tableView:   UITableView, titleForHeaderInSection section: Int) -> String? {
        // new stuff
        return self.sections[section]
        
    }
    
    override func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        if chores.isEmpty {
            return 0
        }
        return chores[section].count
    }
    
    override func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ToDoTableViewCell", for: indexPath) as? ToDoTableViewCell
        let chore = chores[indexPath.section][indexPath.row]

        cell!.nameLabel.text = chore.name
        cell!.dateLabel.text = chore.date
        
        return cell!
    }
    
    override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
        if segue.identifier == "choreDetails" {
            if let destVC = segue.destination as? ChoreViewController {
                let choresToPass = chores[tableView.indexPathForSelectedRow!.section][tableView.indexPathForSelectedRow!.row]
                destVC.choreName = choresToPass.name
                destVC.choreDate = choresToPass.date
                destVC.choreDescription = choresToPass.desc
            }
        }
    }
    
}

