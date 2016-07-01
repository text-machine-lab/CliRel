/************************************************************************/
/*                                                                      */
/*   kernel.h                                                           */
/*                                                                      */
/*   User defined kernel function. Feel free to plug in your own.       */
/*                                                                      */
/*   Copyright: Alessandro Moschitti                                    */
/*   Date: 20.11.06                                                     */
/*                                                                      */
/*   Date: 27.06.16                                                     */
/*   Name: Renan Campos                                                 */
/*   Custom Kernel described in Kim, et al.                             */
/*   "Extracting Clinical Relations in Electronic Health Records        */
/*    Using Enriched Parse Trees" (Kim, et al.)                         */
/*                                                                      */
/*   Compile with svm-light-tk package found here:                      */                                                   
/*   http://disi.unitn.it/moschitti/Tree-Kernel.htm                     */
/*                                                                      */
/************************************************************************/

double custom_kernel(KERNEL_PARM *kernel_parm, DOC *a, DOC *b) 
{

  int i;
  double K_L; // Entity Kernel
  double K_T; // Tree Kernel
   
  double alpha; // Hyperparameter

  alpha = atof(kernel_parm -> custom);

  for(i=0; i < a->num_of_trees && i < b->num_of_trees; i++) // a->num_of_trees should be equal to b->num_of_trees
    if(a->forest_vec[0]!= NULL && b->forest_vec[0]!= NULL)
      K_T = tree_kernel(kernel_parm,a,b,0,0) /
            (tree_kernel(kernel_parm, a,a,0,0)*tree_kernel(kernel_parm,b,b,0,0));
   
  for(i=0; i < a->num_of_vectors && i < b->num_of_vectors; i++)
     if(a->vectors[i]!=NULL && b->vectors[i]!=NULL)
       K_L = pow((a->vectors[i]->words[0].weight == b->vectors[i]->words[0].weight)
           +  (a->vectors[i]->words[1].weight == b->vectors[i]->words[1].weight) + 1, 2) / 9;
  
  return (alpha) * K_L + (1 - alpha) * K_T;
}
